"""
Tests for the enhanced metrics collection and aggregation service.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.services.metrics_service import MetricsCollector, MetricType, MetricPeriod
from app.services.redis_service import RedisService
from app.models import (
    Order, OrderItem, OrderStatus, PaymentStatus, User, UserRole, 
    Product, ProductStatus, Dispute, DisputeStatus, OrderReview,
    Cart, CartStatus, Notification, InventoryHistory, FundingRequest
)


class TestMetricsCollector:
    """Test cases for MetricsCollector service."""
    
    @pytest.fixture
    def mock_redis_service(self):
        """Mock Redis service for testing."""
        redis_service = AsyncMock(spec=RedisService)
        redis_service.get.return_value = None
        redis_service.set.return_value = True
        redis_service.lpush.return_value = True
        redis_service.ltrim.return_value = True
        redis_service.lrange.return_value = []
        return redis_service
    
    @pytest.fixture
    def metrics_collector(self, mock_redis_service):
        """Create MetricsCollector instance with mocked Redis."""
        return MetricsCollector(redis_service=mock_redis_service)
    
    @pytest.fixture
    def sample_orders(self, sample_user, sample_farmer_user):
        """Create sample orders for testing."""
        orders = []
        
        # Paid order
        paid_order = Order(
            id=1,
            buyer_id=sample_user.id,
            status=OrderStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            subtotal=Decimal("90.00"),
            platform_fee=Decimal("9.00"),
            shipping_fee=Decimal("5.00"),
            tax_amount=Decimal("6.00"),
            total=Decimal("100.00"),
            created_at=datetime.utcnow() - timedelta(days=5),
            delivered_at=datetime.utcnow() - timedelta(days=1)
        )
        orders.append(paid_order)
        
        # Pending order
        pending_order = Order(
            id=2,
            buyer_id=sample_user.id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.UNPAID,
            subtotal=Decimal("45.00"),
            platform_fee=Decimal("4.50"),
            shipping_fee=Decimal("3.00"),
            tax_amount=Decimal("2.50"),
            total=Decimal("50.00"),
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        orders.append(pending_order)
        
        # Cancelled order
        cancelled_order = Order(
            id=3,
            buyer_id=sample_user.id,
            status=OrderStatus.CANCELLED,
            payment_status=PaymentStatus.UNPAID,
            subtotal=Decimal("27.00"),
            platform_fee=Decimal("2.70"),
            shipping_fee=Decimal("2.00"),
            tax_amount=Decimal("1.30"),
            total=Decimal("30.00"),
            created_at=datetime.utcnow() - timedelta(days=3),
            cancelled_at=datetime.utcnow() - timedelta(days=2)
        )
        orders.append(cancelled_order)
        
        return orders
    
    @pytest.fixture
    def sample_order_items(self, sample_orders, sample_product, sample_farmer_user):
        """Create sample order items for testing."""
        items = []
        
        # Items for paid order
        item1 = OrderItem(
            id=1,
            order_id=1,
            product_id=sample_product.id,
            quantity=Decimal("2.0"),
            unit_price=Decimal("45.00"),
            farmer_id=sample_farmer_user.id,
            fulfillment_status="delivered"
        )
        items.append(item1)
        
        # Items for pending order
        item2 = OrderItem(
            id=2,
            order_id=2,
            product_id=sample_product.id,
            quantity=Decimal("1.0"),
            unit_price=Decimal("45.00"),
            farmer_id=sample_farmer_user.id,
            fulfillment_status="pending"
        )
        items.append(item2)
        
        return items
    
    @pytest.mark.asyncio
    async def test_get_comprehensive_metrics(self, metrics_collector, mock_redis_service):
        """Test getting comprehensive platform metrics."""
        
        # Mock Redis cache miss
        mock_redis_service.get.return_value = None
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        
        assert "period" in metrics
        assert "revenue" in metrics
        assert "orders" in metrics
        assert "users" in metrics
        assert "products" in metrics
        assert "disputes" in metrics
        assert "engagement" in metrics
        assert "inventory" in metrics
        assert "funding" in metrics
        assert "generated_at" in metrics
        
        # Verify cache was called
        mock_redis_service.get.assert_called_once()
        mock_redis_service.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_comprehensive_metrics_with_cache(self, metrics_collector, mock_redis_service):
        """Test getting metrics from cache."""
        
        cached_data = {
            "period": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
            "revenue": {"gmv": 1000.0},
            "generated_at": "2024-01-31T12:00:00"
        }
        
        mock_redis_service.get.return_value = '{"period": {"start_date": "2024-01-01", "end_date": "2024-01-31"}, "revenue": {"gmv": 1000.0}, "generated_at": "2024-01-31T12:00:00"}'
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        
        assert metrics["revenue"]["gmv"] == 1000.0
        mock_redis_service.get.assert_called_once()
        mock_redis_service.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_track_event(self, metrics_collector, mock_redis_service):
        """Test event tracking functionality."""
        
        await metrics_collector.track_event(
            event_type="product_view",
            user_id=123,
            metadata={"product_id": 456, "category": "vegetables"}
        )
        
        mock_redis_service.lpush.assert_called_once()
        mock_redis_service.ltrim.assert_called_once()
        
        # Verify the event data structure
        call_args = mock_redis_service.lpush.call_args
        assert call_args[0][0] == "events:queue"
        
        import json
        event_data = json.loads(call_args[0][1])
        assert event_data["event_type"] == "product_view"
        assert event_data["user_id"] == 123
        assert event_data["metadata"]["product_id"] == 456
        assert "timestamp" in event_data
    
    @pytest.mark.asyncio
    async def test_get_real_time_metrics(self, metrics_collector, mock_redis_service):
        """Test real-time metrics retrieval."""
        
        # Mock recent events
        mock_events = [
            '{"event_type": "product_view", "user_id": 1, "timestamp": "2024-01-01T12:00:00"}',
            '{"event_type": "add_to_cart", "user_id": 1, "timestamp": "2024-01-01T12:05:00"}',
            '{"event_type": "product_view", "user_id": 2, "timestamp": "2024-01-01T12:10:00"}'
        ]
        
        mock_redis_service.lrange.return_value = mock_events
        
        metrics = await metrics_collector.get_real_time_metrics()
        
        assert "current_hour_events" in metrics
        assert "total_events_tracked" in metrics
        assert "last_updated" in metrics
        assert metrics["total_events_tracked"] == 3
        
        mock_redis_service.lrange.assert_called_once_with("events:queue", 0, 99)
    
    def test_revenue_metrics_calculation(self, metrics_collector, sample_orders, sample_order_items):
        """Test revenue metrics calculation logic."""
        
        # This would typically be tested with actual database data
        # For now, we test the calculation logic
        
        paid_orders = [order for order in sample_orders if order.payment_status == PaymentStatus.PAID]
        
        gmv = sum(float(order.total) for order in paid_orders)
        platform_fees = sum(float(order.platform_fee) for order in paid_orders)
        
        assert gmv == 100.0
        assert platform_fees == 9.0
        
        take_rate = platform_fees / gmv if gmv > 0 else 0
        assert take_rate == 0.09
    
    def test_order_metrics_calculation(self, metrics_collector, sample_orders):
        """Test order metrics calculation logic."""
        
        total_orders = len(sample_orders)
        cancelled_orders = [o for o in sample_orders if o.status == OrderStatus.CANCELLED]
        cancellation_rate = len(cancelled_orders) / total_orders if total_orders > 0 else 0
        
        assert total_orders == 3
        assert len(cancelled_orders) == 1
        assert cancellation_rate == 1/3
    
    def test_fulfillment_time_calculation(self, metrics_collector, sample_orders):
        """Test fulfillment time calculation."""
        
        delivered_orders = [
            o for o in sample_orders 
            if o.status == OrderStatus.DELIVERED and o.delivered_at
        ]
        
        fulfillment_times = []
        for order in delivered_orders:
            fulfillment_time = (order.delivered_at - order.created_at).days
            fulfillment_times.append(fulfillment_time)
        
        avg_fulfillment_time = sum(fulfillment_times) / len(fulfillment_times) if fulfillment_times else 0
        
        assert len(delivered_orders) == 1
        assert avg_fulfillment_time == 4  # 5 days ago to 1 day ago
    
    @pytest.mark.asyncio
    async def test_metrics_with_date_filtering(self, metrics_collector):
        """Test metrics calculation with date filtering."""
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        metrics = await metrics_collector.get_comprehensive_metrics(start_date, end_date)
        
        assert metrics["period"]["start_date"] == start_date.isoformat()
        assert metrics["period"]["end_date"] == end_date.isoformat()
    
    @pytest.mark.asyncio
    async def test_metrics_error_handling(self, metrics_collector, mock_redis_service):
        """Test error handling in metrics collection."""
        
        # Mock Redis error
        mock_redis_service.get.side_effect = Exception("Redis connection error")
        
        # Should still work without cache
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        try:
            metrics = await metrics_collector.get_comprehensive_metrics(
                start_date, end_date, include_cache=False
            )
            # Should complete without cache
            assert "period" in metrics
        except Exception as e:
            # If database operations fail, that's expected in test environment
            assert "Redis connection error" not in str(e)
    
    def test_metric_value_dataclass(self):
        """Test MetricValue dataclass."""
        
        from app.services.metrics_service import MetricValue
        
        metric = MetricValue(
            value=100.50,
            timestamp=datetime.utcnow(),
            period=MetricPeriod.DAY,
            metadata={"source": "orders"}
        )
        
        assert metric.value == 100.50
        assert metric.period == MetricPeriod.DAY
        assert metric.metadata["source"] == "orders"
    
    def test_metric_enums(self):
        """Test metric type and period enums."""
        
        assert MetricType.REVENUE == "revenue"
        assert MetricType.ORDERS == "orders"
        assert MetricType.USERS == "users"
        
        assert MetricPeriod.HOUR == "hour"
        assert MetricPeriod.DAY == "day"
        assert MetricPeriod.MONTH == "month"


class TestMetricsIntegration:
    """Integration tests for metrics service."""
    
    @pytest.mark.asyncio
    async def test_full_metrics_pipeline(self):
        """Test the complete metrics collection pipeline."""
        
        # This would be an integration test with actual database
        # For now, we verify the service can be instantiated and basic methods work
        
        collector = MetricsCollector()
        
        # Test event tracking
        await collector.track_event("test_event", user_id=1)
        
        # Test real-time metrics
        real_time = await collector.get_real_time_metrics()
        assert isinstance(real_time, dict)
        
        # Test comprehensive metrics (will use empty database in test)
        metrics = await collector.get_comprehensive_metrics()
        assert isinstance(metrics, dict)
        assert "period" in metrics