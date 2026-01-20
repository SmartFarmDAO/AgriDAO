"""Tests for AI recommendations feature."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import Product, Order, OrderItem, User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_get_popular_products(client: TestClient, session: Session):
    """Test getting popular products."""
    # Create test products
    products = [
        Product(name="Tomatoes", price=5.0, quantity_available=100, status="active"),
        Product(name="Carrots", price=3.0, quantity_available=50, status="active"),
        Product(name="Lettuce", price=2.0, quantity_available=75, status="active"),
    ]
    for p in products:
        session.add(p)
    session.commit()

    response = client.get("/recommendations/popular?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3


def test_get_trending_products(client: TestClient, session: Session):
    """Test getting trending products."""
    # Create test products
    product = Product(name="Organic Apples", price=10.0, quantity_available=50, status="active")
    session.add(product)
    session.commit()

    response = client.get("/recommendations/trending?days=7&limit=6")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_similar_products(client: TestClient, session: Session):
    """Test getting similar products."""
    # Create products in same category
    products = [
        Product(name="Red Apples", price=10.0, category="Fruits", quantity_available=50, status="active"),
        Product(name="Green Apples", price=12.0, category="Fruits", quantity_available=30, status="active"),
        Product(name="Oranges", price=8.0, category="Fruits", quantity_available=40, status="active"),
    ]
    for p in products:
        session.add(p)
    session.commit()
    session.refresh(products[0])

    response = client.get(f"/recommendations/similar/{products[0].id}?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2
    # Should not include the original product
    assert all(p["id"] != products[0].id for p in data)


def test_recommendations_exclude_out_of_stock(client: TestClient, session: Session):
    """Test that recommendations exclude out of stock products."""
    products = [
        Product(name="In Stock", price=5.0, quantity_available=10, status="active"),
        Product(name="Out of Stock", price=5.0, quantity_available=0, status="active"),
    ]
    for p in products:
        session.add(p)
    session.commit()

    response = client.get("/recommendations/popular?limit=10")
    assert response.status_code == 200
    data = response.json()
    # Should only return in-stock products
    assert all(p["quantity_available"] > 0 for p in data)


def test_recommendations_limit(client: TestClient, session: Session):
    """Test that limit parameter works correctly."""
    # Create 10 products
    for i in range(10):
        product = Product(
            name=f"Product {i}",
            price=5.0 + i,
            quantity_available=10,
            status="active"
        )
        session.add(product)
    session.commit()

    response = client.get("/recommendations/popular?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
