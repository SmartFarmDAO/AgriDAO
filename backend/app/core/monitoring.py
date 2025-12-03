"""
Comprehensive monitoring and alerting system for AgriDAO.
Provides metrics collection, health checks, and alerting capabilities.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import psutil
import redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_logger, log_performance_metric
from app.database import SessionLocal
from app.core.config import settings


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class Alert:
    """Alert configuration and data."""
    name: str
    severity: str  # "info", "warning", "critical"
    message: str
    threshold: float
    current_value: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class HealthChecker:
    """Comprehensive health checking system."""
    
    def __init__(self):
        self.logger = get_logger("health")
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
            except Exception as e:
                self.logger.error(f"Failed to initialize Redis client: {e}")
    
    async def check_database(self) -> HealthCheck:
        """Check database health."""
        start_time = time.time()
        
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="database",
                status="healthy",
                message="Database connection successful",
                response_time_ms=response_time,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="database",
                status="unhealthy",
                message=f"Database connection failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    async def check_redis(self) -> HealthCheck:
        """Check Redis health."""
        start_time = time.time()
        
        if not self.redis_client:
            return HealthCheck(
                name="redis",
                status="degraded",
                message="Redis not configured",
                response_time_ms=0,
                timestamp=datetime.utcnow()
            )
        
        try:
            await self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="redis",
                status="healthy",
                message="Redis connection successful",
                response_time_ms=response_time,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="redis",
                status="unhealthy",
                message=f"Redis connection failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    async def check_disk_space(self) -> HealthCheck:
        """Check disk space usage."""
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            status = "healthy"
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            
            return HealthCheck(
                name="disk_space",
                status=status,
                message=f"Disk usage: {usage_percent:.1f}%",
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={
                    "total_gb": disk_usage.total / (1024**3),
                    "used_gb": disk_usage.used / (1024**3),
                    "free_gb": disk_usage.free / (1024**3),
                    "usage_percent": usage_percent
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="disk_space",
                status="unhealthy",
                message=f"Failed to check disk space: {str(e)}",
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    async def check_memory_usage(self) -> HealthCheck:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            status = "healthy"
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            
            return HealthCheck(
                name="memory",
                status=status,
                message=f"Memory usage: {usage_percent:.1f}%",
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "usage_percent": usage_percent
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="memory",
                status="unhealthy",
                message=f"Failed to check memory usage: {str(e)}",
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    async def check_cpu_usage(self) -> HealthCheck:
        """Check CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            status = "healthy"
            if cpu_percent > 90:
                status = "critical"
            elif cpu_percent > 80:
                status = "warning"
            
            return HealthCheck(
                name="cpu",
                status=status,
                message=f"CPU usage: {cpu_percent:.1f}%",
                response_time_ms=1000,  # 1 second interval
                timestamp=datetime.utcnow(),
                details={"usage_percent": cpu_percent}
            )
            
        except Exception as e:
            return HealthCheck(
                name="cpu",
                status="unhealthy",
                message=f"Failed to check CPU usage: {str(e)}",
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    async def get_all_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all health checks."""
        checks = {}
        
        # Run all checks concurrently
        check_coroutines = [
            self.check_database(),
            self.check_redis(),
            self.check_disk_space(),
            self.check_memory_usage(),
            self.check_cpu_usage(),
        ]
        
        results = await asyncio.gather(*check_coroutines, return_exceptions=True)
        
        check_names = ["database", "redis", "disk_space", "memory", "cpu"]
        
        for name, result in zip(check_names, results):
            if isinstance(result, Exception):
                checks[name] = HealthCheck(
                    name=name,
                    status="unhealthy",
                    message=f"Health check failed: {str(result)}",
                    response_time_ms=0,
                    timestamp=datetime.utcnow(),
                    details={"error": str(result)}
                )
            else:
                checks[name] = result
        
        return checks


class MetricsCollector:
    """Collect and aggregate system metrics."""
    
    def __init__(self):
        self.logger = get_logger("metrics")
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count,
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "usage_percent": memory.percent,
                    "swap_total_gb": psutil.swap_memory().total / (1024**3),
                    "swap_used_gb": psutil.swap_memory().used / (1024**3)
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "usage_percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "process": {
                    "pid": process.pid,
                    "memory_rss_gb": process.memory_info().rss / (1024**3),
                    "memory_vms_gb": process.memory_info().vms / (1024**3),
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                    "num_fds": process.num_fds() if hasattr(process, 'num_fds') else None
                }
            }
            
            # Log metrics
            for category, data in metrics.items():
                if category != "timestamp":
                    for metric_name, value in data.items():
                        if isinstance(value, (int, float)):
                            log_performance_metric(
                                metric_name=f"{category}_{metric_name}",
                                value=value,
                                unit="count" if isinstance(value, int) else "percent"
                            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return {"error": str(e)}


class AlertManager:
    """Manage alerts and notifications."""
    
    def __init__(self):
        self.logger = get_logger("alerts")
        self.active_alerts: Dict[str, Alert] = {}
    
    def check_alerts(self, health_checks: Dict[str, HealthCheck], 
                    metrics: Dict[str, Any]) -> List[Alert]:
        """Check for alert conditions."""
        alerts = []
        
        # Check health check alerts
        for check_name, check in health_checks.items():
            if check.status == "unhealthy":
                alert = Alert(
                    name=f"{check_name}_unhealthy",
                    severity="critical",
                    message=f"{check_name} is unhealthy: {check.message}",
                    threshold=0,
                    current_value=1,
                    timestamp=datetime.utcnow(),
                    details=check.details
                )
                alerts.append(alert)
            elif check.status == "warning":
                alert = Alert(
                    name=f"{check_name}_warning",
                    severity="warning",
                    message=f"{check_name} warning: {check.message}",
                    threshold=80,
                    current_value=85,
                    timestamp=datetime.utcnow(),
                    details=check.details
                )
                alerts.append(alert)
        
        # Check resource usage alerts
        if "memory" in metrics:
            memory_usage = metrics["memory"]["usage_percent"]
            if memory_usage > 90:
                alert = Alert(
                    name="high_memory_usage",
                    severity="critical",
                    message=f"High memory usage: {memory_usage:.1f}%",
                    threshold=90,
                    current_value=memory_usage,
                    timestamp=datetime.utcnow()
                )
                alerts.append(alert)
            elif memory_usage > 80:
                alert = Alert(
                    name="memory_usage_warning",
                    severity="warning",
                    message=f"Memory usage warning: {memory_usage:.1f}%",
                    threshold=80,
                    current_value=memory_usage,
                    timestamp=datetime.utcnow()
                )
                alerts.append(alert)
        
        if "disk" in metrics:
            disk_usage = metrics["disk"]["usage_percent"]
            if disk_usage > 90:
                alert = Alert(
                    name="high_disk_usage",
                    severity="critical",
                    message=f"High disk usage: {disk_usage:.1f}%",
                    threshold=90,
                    current_value=disk_usage,
                    timestamp=datetime.utcnow()
                )
                alerts.append(alert)
            elif disk_usage > 80:
                alert = Alert(
                    name="disk_usage_warning",
                    severity="warning",
                    message=f"Disk usage warning: {disk_usage:.1f}%",
                    threshold=80,
                    current_value=disk_usage,
                    timestamp=datetime.utcnow()
                )
                alerts.append(alert)
        
        # Update active alerts
        for alert in alerts:
            self.active_alerts[alert.name] = alert
            self.logger.warning(
                f"Alert triggered: {alert.name}",
                alert_name=alert.name,
                severity=alert.severity,
                message=alert.message,
                current_value=alert.current_value,
                threshold=alert.threshold
            )
        
        return alerts
    
    def get_active_alerts(self) -> List[Alert]:
        """Get currently active alerts."""
        return list(self.active_alerts.values())
    
    def clear_resolved_alerts(self) -> None:
        """Clear resolved alerts."""
        resolved_alerts = []
        
        for alert_name, alert in list(self.active_alerts.items()):
            # Simple heuristic: alerts older than 1 hour are considered resolved
            if datetime.utcnow() - alert.timestamp > timedelta(hours=1):
                resolved_alerts.append(alert_name)
                self.logger.info(f"Alert resolved: {alert_name}")
        
        for alert_name in resolved_alerts:
            del self.active_alerts[alert_name]


# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
alert_manager = AlertManager()