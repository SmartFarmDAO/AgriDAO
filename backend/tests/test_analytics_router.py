"""
Tests for the analytics router.
"""

import os
import pytest
from datetime import datetime, timedelta
from typing import Dict
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models import User, UserRole
from app.database import engine
from sqlmodel import Session
from app.services.auth import token_manager

class TestAnalyticsRouter:
    """Test cases for analytics router endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def admin_auth_header(self) -> Dict[str, str]:
        """Create admin user and return auth header."""
        with Session(engine) as session:
            # Check if admin user exists
            admin_user = session.query(User).filter(User.role == UserRole.ADMIN).first()
            if not admin_user:
                admin_user = User(
                    role=UserRole.ADMIN,
                    name="Admin User",
                    email="admin@test.com"
                )
                session.add(admin_user)
                session.commit()
                session.refresh(admin_user)
            
            tokens = token_manager.create_tokens(admin_user)
            return {"Authorization": f"Bearer {tokens['access_token']}"}
    
    @pytest.fixture
    def regular_auth_header(self) -> Dict[str, str]:
        """Create regular user and return auth header."""
        with Session(engine) as session:
            # Check if regular user exists
            regular_user = session.query(User).filter(User.role == UserRole.BUYER).first()
            if not regular_user:
                regular_user = User(
                    role=UserRole.BUYER,
                    name="Regular User",
                    email="user@test.com"
                )
                session.add(regular_user)
                session.commit()
                session.refresh(regular_user)
            
            tokens = token_manager.create_tokens(regular_user)
            return {"Authorization": f"Bearer {tokens['access_token']}"}
    
    @pytest.fixture
    def mock_metrics_data(self):
        """Mock comprehensive metrics data."""
        return {
            "period": {
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-01-31T23:59:59"
            },
            "revenue": {
                "gmv": 10000.0,
                "platform_fees": 1000.0,
                "take_rate": 0.1,
                "average_order_value": 50.0,
                "daily_revenue": {
                    "2024-01-01": {"gmv": 100.0, "platform_fees": 10.0, "order_count": 2}
                },
                "top_farmers": [
                    {"farmer_id": 1, "revenue": 500.0, "order_count": 10, "items_sold": 20}
                ]
            },
            "orders": {
                "total_orders": 200,
                "status_breakdown": {"confirmed": 150, "pending": 30, "cancelled": 20},
                "payment_breakdown": {"paid": 170, "unpaid": 30},
                "cancellation_rate": 0.1,
                "daily_orders": {"2024-01-01": 5}
            },
            "users": {
                "total_users": 100,
                "new_users": 10,
                "active_users": 80,
                "role_breakdown": {"buyer": 70, "farmer": 25, "admin": 5},
                "daily_registrations": {"2024-01-01": 2}
            },
            "products": {
                "total_products": 50,
                "new_products": 5,
                "status_breakdown": {"active": 40, "inactive": 10},
                "top_products": [
                    {"product_id": 1, "product_name": "Tomatoes", "quantity_sold": 100, "revenue": 500.0}
                ]
            },
            "disputes": {
                "total_disputes": 5,
                "status_breakdown": {"resolved": 3, "open": 2}
            },
            "engagement": {
                "total_carts": 150,
                "cart_conversion_rate": 0.6,
                "total_reviews": 80,
                "average_rating": 4.2
            },
            "inventory": {
                "inventory_changes": 20,
                "low_stock_products": 5,
                "out_of_stock_products": 2
            },
            "funding": {
                "total_requests": 10,
                "total_amount_requested": 50000.0,
                "total_amount_raised": 30000.0
            },
            "generated_at": "2024-01-31T12:00:00"
        }
    
    def test_get_dashboard_metrics_success(self, client, admin_auth_header, mock_metrics_data):
        """Test successful dashboard metrics retrieval."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            response = client.get("/analytics/dashboard", headers=admin_auth_header)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "data" in data
            assert "generated_at" in data
            assert data["data"]["revenue"]["gmv"] == 10000.0
            assert data["data"]["orders"]["total_orders"] == 200
    
    def test_get_dashboard_metrics_with_date_range(self, client, admin_auth_header, mock_metrics_data):
        """Test dashboard metrics with custom date range."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            start_date = "2024-01-01T00:00:00"
            end_date = "2024-01-31T23:59:59"
            
            response = client.get(
                f"/analytics/dashboard?start_date={start_date}&end_date={end_date}",
                headers=admin_auth_header
            )
            
            assert response.status_code == 200
            mock_collector.get_comprehensive_metrics.assert_called_once()
    
    def test_get_dashboard_metrics_admin_required(self, client, regular_auth_header):
        """Test that dashboard metrics requires admin access."""
        
        response = client.get("/analytics/dashboard", headers=regular_auth_header)
        
        # Expect 403 Forbidden
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
    
    def test_get_real_time_metrics_success(self, client, admin_auth_header):
        """Test successful real-time metrics retrieval."""
        
        mock_real_time_data = {
            "current_hour_events": {
                "product_view": 50,
                "add_to_cart": 20,
                "purchase": 5
            },
            "total_events_tracked": 75,
            "last_updated": "2024-01-31T12:00:00"
        }
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_real_time_metrics.return_value = mock_real_time_data
            mock_collector_class.return_value = mock_collector
            
            response = client.get("/analytics/real-time", headers=admin_auth_header)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["current_hour_events"]["product_view"] == 50
            assert data["total_events_tracked"] == 75
    
    def test_get_revenue_analytics_success(self, client, admin_auth_header, mock_metrics_data):
        """Test successful revenue analytics retrieval."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class, \
             patch('app.routers.analytics._calculate_period_comparison') as mock_comparison:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            mock_comparison.return_value = {
                "current_period": 10000.0,
                "previous_period": 8000.0,
                "growth_rate": 25.0
            }
            
            response = client.get("/analytics/revenue", headers=admin_auth_header)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["gmv"] == 10000.0
            assert data["platform_fees"] == 1000.0
            assert "period_comparison" in data
    
    def test_get_user_analytics_success(self, client, admin_auth_header, mock_metrics_data):
        """Test successful user analytics retrieval."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class, \
             patch('app.routers.analytics._calculate_user_growth_trends') as mock_trends:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            mock_trends.return_value = {
                "new_user_trend": "increasing",
                "retention_trend": "stable"
            }
            
            response = client.get("/analytics/users", headers=admin_auth_header)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_users"] == 100
            assert data["new_users"] == 10
            assert "growth_trends" in data
    
    def test_get_product_analytics_success(self, client, admin_auth_header, mock_metrics_data):
        """Test successful product analytics retrieval."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            response = client.get("/analytics/products?limit=10", headers=admin_auth_header)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_products"] == 50
            assert len(data["top_products"]) <= 10
    
    def test_get_order_analytics_success(self, client, admin_auth_header, mock_metrics_data):
        """Test successful order analytics retrieval."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class, \
             patch('app.routers.analytics._calculate_order_trends') as mock_trends:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            mock_trends.return_value = {
                "order_volume_trend": "increasing",
                "conversion_rate": 0.03
            }
            
            response = client.get("/analytics/orders", headers=admin_auth_header)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_orders"] == 200
            assert "trends" in data
    
    def test_get_farmer_analytics_success(self, client, admin_auth_header, mock_metrics_data):
        """Test successful farmer analytics retrieval."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            response = client.get("/analytics/farmers?limit=5", headers=admin_auth_header)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "top_farmers" in data
            assert len(data["top_farmers"]) <= 5
            assert data["top_farmers"][0]["farmer_id"] == 1
    
    def test_track_analytics_event_success(self, client, admin_auth_header):
        """Test successful event tracking."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.track_event.return_value = None
            mock_collector_class.return_value = mock_collector
            
            # Get CSRF token first (optional, depends on implementation)
            headers = {**admin_auth_header}
            
            # Try getting CSRF token if needed
            csrf_response = client.get("/auth/csrf-token")
            if csrf_response.status_code == 200:
                csrf_token = csrf_response.json().get("csrf_token")
                headers["X-CSRF-Token"] = csrf_token
            
            response = client.post(
                "/analytics/track-event",
                params={
                    "event_type": "product_view",
                    "user_id": 123
                },
                json={"product_id": 456},
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            mock_collector.track_event.assert_called_once()
    
    def test_export_analytics_data_csv(self, client, admin_auth_header, mock_metrics_data):
        """Test CSV export functionality."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            response = client.get("/analytics/export?format=csv&metric_type=revenue", headers=admin_auth_header)
            
            assert response.status_code == 200
            assert "text/csv" in response.headers["content-type"]
    
    def test_export_analytics_data_json(self, client, admin_auth_header, mock_metrics_data):
        """Test JSON export functionality."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            response = client.get("/analytics/export?format=json&metric_type=comprehensive", headers=admin_auth_header)
            
            assert response.status_code == 200
            assert "application/json" in response.headers["content-type"]
    
    def test_clear_analytics_cache_success(self, client, admin_auth_header):
        """Test cache clearing functionality."""
        
        response = client.delete("/analytics/cache?pattern=metrics:*", headers=admin_auth_header)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "Cache cleared" in data["message"]
    
    def test_analytics_error_handling(self, client, admin_auth_header):
        """Test error handling in analytics endpoints."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.side_effect = Exception("Database error")
            mock_collector_class.return_value = mock_collector
            
            response = client.get("/analytics/dashboard", headers=admin_auth_header)
            
            assert response.status_code == 500
            assert "Failed to retrieve dashboard metrics" in response.json()["detail"]
    
    def test_date_range_validation(self, client, admin_auth_header, mock_metrics_data):
        """Test date range parameter validation."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            
            # Test with invalid date format
            response = client.get("/analytics/dashboard?start_date=invalid-date", headers=admin_auth_header)
            
            # Should handle gracefully or return validation error
            assert response.status_code in [200, 422]  # Either works or validation error
    
    def test_granularity_parameter(self, client, admin_auth_header, mock_metrics_data):
        """Test granularity parameter validation."""
        
        with patch('app.routers.analytics.MetricsCollector') as mock_collector_class, \
             patch('app.routers.analytics._calculate_period_comparison') as mock_comparison:
            
            mock_collector = AsyncMock()
            mock_collector.get_comprehensive_metrics.return_value = mock_metrics_data
            mock_collector_class.return_value = mock_collector
            mock_comparison.return_value = {}
            
            # Test valid granularity
            response = client.get("/analytics/revenue?granularity=day", headers=admin_auth_header)
            assert response.status_code == 200
            
            # Test invalid granularity
            response = client.get("/analytics/revenue?granularity=invalid", headers=admin_auth_header)
            # Assuming 422 or 400 for invalid enum
            assert response.status_code in [400, 422]