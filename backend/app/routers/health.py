from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
import redis
import psutil
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # System resources
    health_status["checks"]["cpu_percent"] = psutil.cpu_percent()
    health_status["checks"]["memory_percent"] = psutil.virtual_memory().percent
    health_status["checks"]["disk_percent"] = psutil.disk_usage('/').percent
    
    return health_status

@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    # Check if app is ready to serve traffic
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Not ready")

@router.get("/liveness")
async def liveness_check():
    # Simple liveness check
    return {"status": "alive"}
