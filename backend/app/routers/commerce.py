import os
from typing import List, Optional

import stripe
from fastapi import APIRouter, HTTPException, Request, Header, Depends
import jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from ..database import engine
from ..models import Order, OrderItem, Product, PaymentEvent, User
from ..deps import get_current_user


router = APIRouter()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
stripe.api_key = STRIPE_SECRET_KEY or None

PLATFORM_FEE_RATE = float(os.getenv("PLATFORM_FEE_RATE", "0.08"))


class CartItem(BaseModel):
    product_id: int
    quantity: float


class CreateCheckoutPayload(BaseModel):
    items: List[CartItem]
    success_url: str
    cancel_url: str


@router.post("/checkout_session")
def create_checkout_session(payload: CreateCheckoutPayload, authorization: Optional[str] = Header(None)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    # Require JWT and extract buyer_id
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        claims = jwt.decode(token, os.getenv("JWT_SECRET", "devsecret"), algorithms=["HS256"])
        buyer_id = int(claims.get("sub"))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid token")

    with Session(engine) as session:
        # fetch products and calculate totals
        product_map = {p.id: p for p in session.exec(select(Product)).all()}
        if any(item.product_id not in product_map for item in payload.items):
            raise HTTPException(status_code=400, detail="Invalid product in cart")

        subtotal = 0.0
        line_items = []
        for item in payload.items:
            product = product_map[item.product_id]
            amount = product.price * item.quantity
            subtotal += amount
            line_items.append({
                "quantity": int(item.quantity),
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(product.price * 100),
                    "product_data": {"name": product.name},
                },
            })

        platform_fee = round(subtotal * PLATFORM_FEE_RATE, 2)
        total = subtotal + platform_fee

        # create Order and OrderItems
        order = Order(buyer_id=buyer_id, subtotal=subtotal, platform_fee=platform_fee, total=total)
        session.add(order)
        session.commit()
        session.refresh(order)

        for item in payload.items:
            product = product_map[item.product_id]
            session.add(OrderItem(order_id=order.id, product_id=product.id, quantity=item.quantity, unit_price=product.price))
        session.commit()

        # create Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                mode="payment",
                line_items=line_items + [
                    {
                        "quantity": 1,
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(platform_fee * 100),
                            "product_data": {"name": "Platform Fee"},
                        },
                    }
                ],
                success_url=payload.success_url + f"?order_id={order.id}",
                cancel_url=payload.cancel_url + f"?order_id={order.id}",
                metadata={"order_id": str(order.id)},
            )
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(e))

        order.stripe_checkout_session_id = checkout_session.get("id")
        session.add(order)
        session.commit()

        return {"checkout_url": checkout_session.get("url"), "order_id": order.id}


@router.post("/stripe_webhook")
async def stripe_webhook(request: Request):
    raw_body = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    event = None

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload=raw_body, sig_header=sig_header, secret=endpoint_secret
            )
        else:
            # Fallback: parse as JSON
            event = stripe.Event.construct_from(await request.json(), stripe.api_key)  # type: ignore[arg-type]
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(e))

    with Session(engine) as session:
        event_type = event["type"]
        data = event["data"]["object"]
        order_id = int(data.get("metadata", {}).get("order_id", 0)) if isinstance(data, dict) else 0
        session.add(PaymentEvent(order_id=order_id, type=event_type, payload=str(event)))
        session.commit()

        if event_type == "checkout.session.completed":
            # mark order paid
            order = session.get(Order, order_id)
            if order:
                order.payment_status = "paid"
                order.stripe_payment_intent_id = data.get("payment_intent") if isinstance(data, dict) else None
                session.add(order)
                session.commit()

    return {"received": True}


@router.get("/orders")
def list_my_orders(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        orders = session.exec(select(Order).where(Order.buyer_id == current_user.id).order_by(Order.created_at.desc())).all()
        return [
            {
                "id": o.id,
                "status": o.status,
                "subtotal": o.subtotal,
                "platform_fee": o.platform_fee,
                "total": o.total,
                "payment_status": o.payment_status,
                "created_at": o.created_at.isoformat(),
            }
            for o in orders
        ]


@router.get("/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        order = session.get(Order, order_id)
        if not order or order.buyer_id != current_user.id:
            raise HTTPException(status_code=404, detail="Order not found")
        items = session.exec(select(OrderItem).where(OrderItem.order_id == order.id)).all()
        # join product names
        product_ids = [it.product_id for it in items]
        products = {p.id: p for p in session.exec(select(Product).where(Product.id.in_(product_ids))).all()}  # type: ignore[arg-type]
        return {
            "id": order.id,
            "status": order.status,
            "subtotal": order.subtotal,
            "platform_fee": order.platform_fee,
            "total": order.total,
            "payment_status": order.payment_status,
            "created_at": order.created_at.isoformat(),
            "items": [
                {
                    "product_id": it.product_id,
                    "product_name": products.get(it.product_id).name if products.get(it.product_id) else None,
                    "quantity": it.quantity,
                    "unit_price": it.unit_price,
                }
                for it in items
            ],
        }


