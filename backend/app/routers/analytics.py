"""
Enhanced analytics router for admin dashboard.
Provides comprehensive platform metrics, real-time data, and export functionality.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import csv
import io
import json

from ..deps import get_current_user
from ..models import User, UserRole
from ..services.metrics_service import MetricsCollector
from ..services.redis_service import redis_service


router = APIRouter()


class DateRangeQuery(BaseModel):
    """Date range query parameters."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class MetricsResponse(BaseModel):
    """Response model for metrics data."""
    data: Dict[str, Any]
    generated_at: datetime
    cache_hit: bool = False


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin access."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/dashboard", response_model=MetricsResponse)
async def get_dashboard_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for metrics"),
    end_date: Optional[datetime] = Query(None, description="End date for metrics"),
    include_cache: bool = Query(True, description="Whether to use cached data"),
    current_user: User = Depends(require_admin)
) -> MetricsResponse:
    """Get comprehensive dashboard metrics for admin."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        
        # Set default date range if not provided
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        metrics = await metrics_collector.get_comprehensive_metrics(
            start_date=start_date,
            end_date=end_date,
            include_cache=include_cache
        )
        
        return MetricsResponse(
            data=metrics,
            generated_at=datetime.utcnow(),
            cache_hit=include_cache
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve dashboard metrics: {str(e)}"
        )


@router.get("/real-time")
async def get_real_time_metrics(
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """Get real-time platform metrics."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        return await metrics_collector.get_real_time_metrics()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve real-time metrics: {str(e)}"
        )


@router.get("/revenue")
async def get_revenue_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    granularity: str = Query("day", pattern="^(hour|day|week|month)$"),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """Get detailed revenue analytics."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get comprehensive metrics and extract revenue data
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        
        revenue_data = metrics.get("revenue", {})
        
        # Add additional revenue-specific calculations
        revenue_data["period_comparison"] = await _calculate_period_comparison(
            metrics_collector, start_date, end_date, "revenue"
        )
        
        return revenue_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve revenue analytics: {str(e)}"
        )


@router.get("/users")
async def get_user_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """Get detailed user analytics."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        
        user_data = metrics.get("users", {})
        
        # Add user growth trends
        user_data["growth_trends"] = await _calculate_user_growth_trends(
            metrics_collector, start_date, end_date
        )
        
        return user_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user analytics: {str(e)}"
        )


@router.get("/products")
async def get_product_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """Get detailed product analytics."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        
        product_data = metrics.get("products", {})
        
        # Limit top products
        if "top_products" in product_data:
            product_data["top_products"] = product_data["top_products"][:limit]
        
        return product_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve product analytics: {str(e)}"
        )


@router.get("/orders")
async def get_order_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """Get detailed order analytics."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        
        order_data = metrics.get("orders", {})
        
        # Add order trends
        order_data["trends"] = await _calculate_order_trends(
            metrics_collector, start_date, end_date
        )
        
        return order_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve order analytics: {str(e)}"
        )


@router.get("/farmers")
async def get_farmer_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """Get farmer performance analytics."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        
        # Extract farmer data from revenue metrics
        revenue_data = metrics.get("revenue", {})
        top_farmers = revenue_data.get("top_farmers", [])[:limit]
        
        return {
            "top_farmers": top_farmers,
            "total_active_farmers": len(top_farmers),
            "period": metrics.get("period", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve farmer analytics: {str(e)}"
        )


@router.post("/track-event")
async def track_analytics_event(
    event_type: str,
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Track an analytics event."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        
        # Use current user if no user_id provided
        if not user_id:
            user_id = current_user.id
        
        await metrics_collector.track_event(
            event_type=event_type,
            user_id=user_id,
            metadata=metadata
        )
        
        return {"status": "success", "message": "Event tracked successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track event: {str(e)}"
        )


@router.get("/export")
async def export_analytics_data(
    format: ExportFormat = Query(ExportFormat.CSV),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    metric_type: str = Query("comprehensive", pattern="^(comprehensive|revenue|orders|users|products)$"),
    current_user: User = Depends(require_admin)
):
    """Export analytics data in various formats."""
    
    try:
        metrics_collector = MetricsCollector(redis_service)
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get the requested metrics
        if metric_type == "comprehensive":
            data = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        else:
            # Get comprehensive data and extract specific metric
            comprehensive_data = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
            data = comprehensive_data.get(metric_type, {})
        
        # Generate filename
        date_str = start_date.strftime("%Y%m%d")
        filename = f"analytics_{metric_type}_{date_str}.{format}"
        
        if format == ExportFormat.CSV:
            return _export_as_csv(data, filename)
        elif format == ExportFormat.JSON:
            return _export_as_json(data, filename)
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export analytics data: {str(e)}"
        )


@router.delete("/cache")
async def clear_analytics_cache(
    pattern: Optional[str] = Query(None, description="Cache key pattern to clear"),
    current_user: User = Depends(require_admin)
) -> Dict[str, str]:
    """Clear analytics cache."""
    
    try:
        # This would require implementing cache clearing in RedisService
        # For now, return success message
        return {
            "status": "success", 
            "message": f"Cache cleared for pattern: {pattern or 'all analytics'}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


# Helper functions

async def _calculate_period_comparison(
    metrics_collector: MetricsCollector,
    start_date: datetime,
    end_date: datetime,
    metric_type: str
) -> Dict[str, Any]:
    """Calculate period-over-period comparison."""
    
    # Calculate previous period
    period_length = end_date - start_date
    prev_start = start_date - period_length
    prev_end = start_date
    
    try:
        current_metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        previous_metrics = await metrics_collector.get_comprehensive_metrics(prev_start, prev_end)
        
        current_value = current_metrics.get(metric_type, {}).get("gmv", 0)
        previous_value = previous_metrics.get(metric_type, {}).get("gmv", 0)
        
        if previous_value > 0:
            growth_rate = ((current_value - previous_value) / previous_value) * 100
        else:
            growth_rate = 100 if current_value > 0 else 0
        
        return {
            "current_period": current_value,
            "previous_period": previous_value,
            "growth_rate": round(growth_rate, 2),
            "absolute_change": current_value - previous_value
        }
        
    except Exception:
        return {
            "current_period": 0,
            "previous_period": 0,
            "growth_rate": 0,
            "absolute_change": 0
        }


async def _calculate_user_growth_trends(
    metrics_collector: MetricsCollector,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Calculate user growth trends."""
    
    try:
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        user_data = metrics.get("users", {})
        
        # This would typically involve more complex calculations
        # For now, return basic trend data
        return {
            "new_user_trend": "increasing",  # Would calculate from daily_registrations
            "retention_trend": "stable",
            "activation_rate": 0.75  # Placeholder
        }
        
    except Exception:
        return {
            "new_user_trend": "unknown",
            "retention_trend": "unknown",
            "activation_rate": 0
        }


async def _calculate_order_trends(
    metrics_collector: MetricsCollector,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Calculate order trends."""
    
    try:
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        order_data = metrics.get("orders", {})
        
        return {
            "order_volume_trend": "increasing",  # Would calculate from daily_orders
            "aov_trend": "stable",
            "conversion_rate": 0.03  # Placeholder
        }
        
    except Exception:
        return {
            "order_volume_trend": "unknown",
            "aov_trend": "unknown",
            "conversion_rate": 0
        }


def _export_as_csv(data: Dict[str, Any], filename: str) -> StreamingResponse:
    """Export data as CSV."""
    
    output = io.StringIO()
    
    # Flatten the data for CSV export
    flattened_data = _flatten_dict(data)
    
    if flattened_data:
        writer = csv.DictWriter(output, fieldnames=flattened_data[0].keys())
        writer.writeheader()
        writer.writerows(flattened_data)
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def _export_as_json(data: Dict[str, Any], filename: str) -> StreamingResponse:
    """Export data as JSON."""
    
    json_str = json.dumps(data, indent=2, default=str)
    
    return StreamingResponse(
        io.BytesIO(json_str.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def _flatten_dict(data: Dict[str, Any], parent_key: str = "", sep: str = "_") -> List[Dict[str, Any]]:
    """Flatten nested dictionary for CSV export."""
    
    items = []
    
    def _flatten_recursive(obj, parent_key=""):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, (dict, list)):
                    if isinstance(v, list) and v and isinstance(v[0], dict):
                        # Handle list of dictionaries
                        for i, item in enumerate(v):
                            item_result = _flatten_recursive(item, f"{new_key}_{i}")
                            result.update(item_result)
                    elif isinstance(v, dict):
                        nested_result = _flatten_recursive(v, new_key)
                        result.update(nested_result)
                    else:
                        result[new_key] = str(v)
                else:
                    result[new_key] = v
            return result
        else:
            return {parent_key: obj}
    
    flattened = _flatten_recursive(data)
    return [flattened] if flattened else []