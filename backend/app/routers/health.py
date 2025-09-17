import time
import psutil
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from ..database import get_db
from ..services.redis_service import redis_service
from ..core.logging import get_logger

router = APIRouter(tags=["health"])
logger = get_logger("health")


@router.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Comprehensive health check with service status."""
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "system": {},
        "response_time_ms": 0
    }
    
    # Check database connectivity
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = {
            "status": "healthy",
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Redis connectivity
    try:
        redis_start = time.time()
        await redis_service.ping()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "response_time_ms": round((time.time() - redis_start) * 1000, 2)
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # System metrics
    try:
        health_status["system"] = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else None
        }
    except Exception as e:
        logger.warning(f"Could not collect system metrics: {str(e)}")
    
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # Log health check
    logger.info(
        f"Health check completed - Status: {health_status['status']}",
        **health_status["services"]
    )
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@router.get("/health/readiness")
def readiness_check() -> Dict[str, Any]:
    """Readiness probe for Kubernetes/container orchestration."""
    try:
        # Check critical services
        db = next(get_db())
        db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/health/liveness")
def liveness_check() -> Dict[str, Any]:
    """Liveness probe for Kubernetes/container orchestration."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - psutil.Process().create_time()
    }

