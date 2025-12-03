import os
from typing import Dict, Any

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database import engine
from app.models import User, Product, Order, OrderItem


JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")


def make_token(user_id: int) -> str:
    payload = {"sub": str(user_id)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


@pytest.fixture()
def auth_header() -> Dict[str, str]:
    # Ensure a buyer user exists
    with Session(engine) as session:
        user = session.query(User).filter(User.role == "buyer").first()  # type: ignore
        if not user:
            user = User(role="buyer", name="Buyer One", email="buyer1@example.com")
            session.add(user)
            session.commit()
            session.refresh(user)
    token = make_token(user.id)  # type: ignore[arg-type]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def ensure_products() -> None:
    with Session(engine) as session:
        existing = session.query(Product).first()  # type: ignore
        if not existing:
            session.add_all(
                [
                    Product(name="Tomatoes", price=5.0, quantity="100 kg"),
                    Product(name="Rice", price=2.0, quantity="500 kg"),
                ]
            )
            session.commit()


def test_checkout_session_creates_order_and_calls_stripe(client: TestClient, auth_header: Dict[str, str], ensure_products: None, monkeypatch: pytest.MonkeyPatch):
    # Arrange: fetch product ids
    with Session(engine) as session:
        products = session.query(Product).all()  # type: ignore
        p1 = products[0]
        p2 = products[1] if len(products) > 1 else products[0]

    # Mock Stripe checkout create
    called: Dict[str, Any] = {}

    class DummyCheckoutSession(dict):
        def get(self, k, default=None):  # behave like stripe object minimal
            return super().get(k, default)

    def fake_create(**kwargs):
        called["kwargs"] = kwargs
        return DummyCheckoutSession({"id": "cs_test_123", "url": "https://stripe.test/checkout/cs_test_123"})

    import stripe

    # Ensure API key is set to pass the runtime check in the route
    monkeypatch.setattr(stripe, "api_key", "sk_test_dummy")
    monkeypatch.setattr(stripe.checkout.Session, "create", fake_create)

    # Act: call our endpoint
    payload = {
        "items": [
            {"product_id": p1.id, "quantity": 2},
            {"product_id": p2.id, "quantity": 1},
        ],
        "success_url": "http://localhost/success",
        "cancel_url": "http://localhost/cancel",
    }
    resp = client.post("/commerce/checkout_session", json=payload, headers=auth_header)

    # Assert
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["checkout_url"].startswith("https://")
    assert body["order_id"]

    # Check we created Order and OrderItems
    with Session(engine) as session:
        order = session.get(Order, body["order_id"])  # type: ignore[arg-type]
        assert order is not None
        items = session.query(OrderItem).filter(OrderItem.order_id == order.id).all()  # type: ignore
        assert len(items) >= 2

    # Stripe create called with expected fee line appended
    assert "line_items" in called["kwargs"]
    assert any(li["price_data"]["product_data"]["name"] == "Platform Fee" for li in called["kwargs"]["line_items"])  # type: ignore[index]


def test_list_and_get_orders_requires_auth_and_returns_orders(client: TestClient, auth_header: Dict[str, str]):
    # list my orders
    r = client.get("/commerce/orders", headers=auth_header)
    assert r.status_code == 200
    orders = r.json()

    if orders:
        oid = orders[0]["id"]
        r2 = client.get(f"/commerce/orders/{oid}", headers=auth_header)
        assert r2.status_code == 200
        data = r2.json()
        assert data["id"] == oid
        assert isinstance(data["items"], list)

    # missing auth
    r3 = client.get("/commerce/orders")
    assert r3.status_code in (401, 403)
