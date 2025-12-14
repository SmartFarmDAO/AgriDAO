import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import User, Product

client = TestClient(app)

class TestAPI:
    def test_health_endpoint(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        
    def test_user_registration(self):
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        
    def test_product_listing(self):
        response = client.get("/api/products")
        assert response.status_code == 200
        assert "products" in response.json()
        
    def test_unauthorized_access(self):
        response = client.post("/api/products", json={"name": "Test Product"})
        assert response.status_code == 401
