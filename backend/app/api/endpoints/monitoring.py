"""
Monitoring and health check API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.monitoring import (
    health_checker, 
    metrics_collector, 
    alert_manager,
    HealthCheck,
    Alert
)
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health", response_model=Dict[str, Any])
async def get_health_status() -> Dict[str, Any]:
    """
    Get comprehensive health status of all system components.
    
    Returns:
        Dictionary containing health checks for all system components
    """
    health_checks = await health_checker.get_all_health_checks()
    
    # Convert HealthCheck objects to dict
    checks_dict = {}
    for name, check in health_checks.items():
        checks_dict[name] = {
            "name": check.name,
            "status": check.status,
            "message": check.message,
            "response_time_ms": check.response_time_ms,
            "timestamp": check.timestamp.isoformat(),
            "details": check.details
        }
    
    # Overall status
    unhealthy_count = sum(1 for check in health_checks.values() 
                         if check.status == "unhealthy")
    warning_count = sum(1 for check in health_checks.values() 
                       if check.status == "warning")
    
    overall_status = "healthy"
    if unhealthy_count > 0:
        overall_status = "unhealthy"
    elif warning_count > 0:
        overall_status = "warning"
    
    return {
        "overall_status": overall_status,
        "checks": checks_dict,
        "summary": {
            "total_checks": len(health_checks),
            "healthy": len([c for c in health_checks.values() if c.status == "healthy"]),
            "warning": warning_count,
            "unhealthy": unhealthy_count
        }
    }


@router.get("/metrics", response_model=Dict[str, Any])
async def get_system_metrics() -> Dict[str, Any]:
    """
    Get current system metrics.
    
    Returns:
        Dictionary containing system metrics
    """
    metrics = metrics_collector.collect_system_metrics()
    return metrics


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_active_alerts() -> List[Dict[str, Any]]:
    """
    Get currently active system alerts.
    
    Returns:
        List of active alerts
    """
    alerts = alert_manager.get_active_alerts()
    
    # Convert Alert objects to dict
    return [
        {
            "name": alert.name,
            "severity": alert.severity,
            "message": alert.message,
            "threshold": alert.threshold,
            "current_value": alert.current_value,
            "timestamp": alert.timestamp.isoformat(),
            "details": alert.details
        }
        for alert in alerts
    ]


@router.post("/alerts/clear")
async def clear_resolved_alerts(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Clear resolved alerts (admin only).
    
    Args:
        current_user: Currently authenticated user
    
    Returns:
        Success message
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    alert_manager.clear_resolved_alerts()
    return {"message": "Resolved alerts cleared"}


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive system status including health, metrics, and alerts.
    
    Returns:
        Complete system status information
    """
    health_status = await get_health_status()
    metrics = await get_system_metrics()
    alerts = await get_active_alerts()
    
    return {
        "health": health_status,
        "metrics": metrics,
        "alerts": alerts,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint for basic connectivity check.
    
    Returns:
        Pong response
    """
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}