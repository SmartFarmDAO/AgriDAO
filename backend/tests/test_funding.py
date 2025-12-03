"""Tests for funding request feature."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import FundingRequest


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
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
    """Create a test client."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_funding_request(client: TestClient):
    """Test creating a funding request."""
    response = client.post(
        "/finance/requests",
        json={
            "farmer_name": "John Doe",
            "purpose": "Buy organic seeds",
            "amount_needed": 1000.0,
            "amount_raised": 0.0,
            "days_left": 30,
            "category": "Seeds & Supplies",
            "location": "California",
            "description": "Need funding for organic vegetable seeds",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["farmer_name"] == "John Doe"
    assert data["purpose"] == "Buy organic seeds"
    assert data["amount_needed"] == 1000.0
    assert data["amount_raised"] == 0.0


def test_list_funding_requests(client: TestClient, session: Session):
    """Test listing funding requests."""
    # Create test funding requests
    request1 = FundingRequest(
        farmer_name="Alice",
        purpose="Equipment",
        amount_needed=2000.0,
        amount_raised=500.0,
        days_left=20,
    )
    request2 = FundingRequest(
        farmer_name="Bob",
        purpose="Infrastructure",
        amount_needed=5000.0,
        amount_raised=1000.0,
        days_left=45,
    )
    session.add(request1)
    session.add(request2)
    session.commit()

    response = client.get("/finance/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_donate_to_request(client: TestClient, session: Session):
    """Test donating to a funding request."""
    # Create a funding request
    request = FundingRequest(
        farmer_name="Charlie",
        purpose="Emergency supplies",
        amount_needed=1000.0,
        amount_raised=0.0,
        days_left=15,
    )
    session.add(request)
    session.commit()
    session.refresh(request)

    # Donate to the request
    response = client.post(
        f"/finance/requests/{request.id}/donate",
        json={"amount": 250.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount_raised"] == 250.0


def test_donate_invalid_amount(client: TestClient, session: Session):
    """Test donating with invalid amount."""
    request = FundingRequest(
        farmer_name="Dave",
        purpose="Seeds",
        amount_needed=500.0,
        amount_raised=0.0,
        days_left=10,
    )
    session.add(request)
    session.commit()
    session.refresh(request)

    # Try to donate negative amount
    response = client.post(
        f"/finance/requests/{request.id}/donate",
        json={"amount": -100.0},
    )
    assert response.status_code == 400


def test_funding_milestone_completion(client: TestClient, session: Session):
    """Test funding request completion."""
    request = FundingRequest(
        farmer_name="Eve",
        purpose="Farm expansion",
        amount_needed=1000.0,
        amount_raised=0.0,
        days_left=30,
    )
    session.add(request)
    session.commit()
    session.refresh(request)

    # Donate full amount
    response = client.post(
        f"/finance/requests/{request.id}/donate",
        json={"amount": 1000.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount_raised"] == 1000.0
    assert data["status"] == "Funded"


def test_get_finance_metrics(client: TestClient):
    """Test getting finance metrics."""
    response = client.get("/finance/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "gmv" in data
    assert "fee_revenue" in data
    assert "orders_total" in data
    assert "orders_paid" in data
    assert "take_rate" in data
