import os
from typing import Dict

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database import engine
from app.models import Order

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")


def make_token(user_id: int) -> str:
    payload = {"sub": str(user_id)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


@pytest.fixture()
def order_ready(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> int:
    # Create an order via checkout (stripe create mocked)
    from sqlmodel import select
    from app.models import User, Product

    # ensure buyer and product exist
    with Session(engine) as session:
        buyer = session.exec(select(User).where(User.role == "buyer")).first()
        if not buyer:
            buyer = User(role="buyer", name="Buyer", email="b@example.com")
            session.add(buyer)
            session.commit()
            session.refresh(buyer)
        product = session.exec(select(Product)).first()
        if not product:
            product = Product(name="Corn", price=1.5, quantity="10 kg")
            session.add(product)
            session.commit()
            session.refresh(product)
        token = make_token(buyer.id)  # type: ignore[arg-type]

    called = {}

    class DummyCheckout(dict):
        def get(self, k, default=None):
            return super().get(k, default)

    def fake_create(**kwargs):
        called["kwargs"] = kwargs
        return DummyCheckout({"id": "cs_test_abc", "url": "https://stripe.test/checkout/cs_test_abc"})

    import stripe

    monkeypatch.setattr(stripe, "api_key", "sk_test_dummy")
    monkeypatch.setattr(stripe.checkout.Session, "create", fake_create)

    payload = {
        "items": [{"product_id": product.id, "quantity": 1}],
        "success_url": "http://localhost/success",
        "cancel_url": "http://localhost/cancel",
    }
    r = client.post("/commerce/checkout_session", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    return r.json()["order_id"]


def test_webhook_marks_order_paid(client: TestClient, order_ready: int, monkeypatch: pytest.MonkeyPatch):
    # Prepare a fake event when no STRIPE_WEBHOOK_SECRET is set
    os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {"order_id": str(order_ready)},
                "payment_intent": "pi_test_123",
            }
        },
    }

    # stripe.Event.construct_from requires an api key; ensure set
    import stripe

    monkeypatch.setattr(stripe, "api_key", "sk_test_dummy")

    r = client.post("/commerce/stripe_webhook", json=event, headers={"content-type": "application/json"})
    assert r.status_code == 200, r.text
    assert r.json().get("received") is True

    # Verify order paid
    with Session(engine) as session:
        order = session.get(Order, order_ready)
        assert order is not None
        assert order.payment_status == "paid"
        assert order.stripe_payment_intent_id == "pi_test_123"
