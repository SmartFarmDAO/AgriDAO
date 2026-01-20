import os
from typing import List, Optional, Dict, Any

import stripe
from fastapi import APIRouter, HTTPException, Request, Header, Depends
import jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from ..database import engine
from ..models import Order, OrderItem, Product, PaymentEvent, User
from ..deps import get_current_user
from ..services.checkout_service import CheckoutValidator
from ..services.cart_service import CartService
from ..services.payment_service import PaymentService


router = APIRouter()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
stripe.api_key = STRIPE_SECRET_KEY or None

PLATFORM_FEE_RATE = float(os.getenv("PLATFORM_FEE_RATE", "0.08"))

# Initialize services
checkout_validator = CheckoutValidator()
cart_service = CartService()
payment_service = PaymentService()


class CartItem(BaseModel):
    product_id: int
    quantity: float


class CreateCheckoutPayload(BaseModel):
    items: List[CartItem]
    success_url: str
    cancel_url: str


class CreateCheckoutSessionRequest(BaseModel):
    cart_id: int
    shipping_address: Dict[str, Any]
    success_url: str
    cancel_url: str


class ValidateCheckoutRequest(BaseModel):
    cart_id: int
    shipping_address: Optional[Dict[str, Any]] = None


@router.post("/checkout_session")
def create_checkout_session(payload: CreateCheckoutPayload, authorization: Optional[str] = Header(None)):
    if not stripe.api_key:
        print("MOCK CHECKOUT: Stripe key missing, proceeding with order creation")
        # Continue to create order first, then return mock URL


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
                    "currency": "bdt",
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

        if not stripe.api_key:
            print("MOCK CHECKOUT: Stripe key missing, returning mock success URL")
            # For mock checkout, we skip Stripe session creation but keep the order
            order.stripe_checkout_session_id = "mock_session_123"
            session.add(order)
            session.commit()
            return {"checkout_url": f"{payload.success_url}?session_id=mock_session_123", "order_id": order.id}

        # create Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                mode="payment",
                line_items=line_items + [
                    {
                        "quantity": 1,
                        "price_data": {
                            "currency": "bdt",
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


@router.post("/validate_checkout")
def validate_checkout(
    request: ValidateCheckoutRequest,
    current_user: User = Depends(get_current_user)
):
    """Validate checkout data before creating payment session."""
    
    # Validate user eligibility
    user_validation = checkout_validator.validate_user_eligibility(current_user.id)
    if not user_validation["valid"]:
        raise HTTPException(status_code=400, detail=user_validation["message"])
    
    # Validate inventory
    inventory_validation = checkout_validator.validate_inventory(request.cart_id)
    if not inventory_validation["valid"]:
        raise HTTPException(status_code=400, detail=inventory_validation)
    
    # Validate pricing
    pricing_validation = checkout_validator.validate_pricing(request.cart_id)
    if not pricing_validation["valid"]:
        raise HTTPException(status_code=400, detail=pricing_validation)
    
    response = {
        "valid": True,
        "pricing": pricing_validation["pricing"],
        "cart_summary": cart_service.get_cart_summary(request.cart_id)
    }
    
    # Validate shipping address if provided
    if request.shipping_address:
        address_validation = checkout_validator.validate_shipping_address(request.shipping_address)
        if not address_validation["valid"]:
            response["address_validation"] = address_validation
        else:
            response["formatted_address"] = address_validation["formatted_address"]
    
    return response


@router.post("/checkout_session_v2")
def create_checkout_session_v2(
    request: CreateCheckoutSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create checkout session with comprehensive validation."""
    
    # Create checkout session with validation
    session_result = checkout_validator.create_checkout_session(
        user_id=current_user.id,
        cart_id=request.cart_id,
        shipping_address=request.shipping_address
    )
    
    if not session_result["valid"]:
        raise HTTPException(status_code=400, detail=session_result)
    
    checkout_session_data = session_result["checkout_session"]
    
    # Get cart items for Stripe
    cart_items = cart_service.get_cart_items(request.cart_id)
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Create Stripe line items
    line_items = []
    for item in cart_items:
        line_items.append({
            "quantity": item["quantity"],
            "price_data": {
                "currency": "bdt",
                "unit_amount": int(item["unit_price"] * 100),
                "product_data": {"name": item["product_name"]},
            },
        })
    
    # Add platform fee
    pricing = checkout_session_data["pricing"]
    line_items.append({
        "quantity": 1,
        "price_data": {
            "currency": "bdt",
            "unit_amount": int(pricing["platform_fee"] * 100),
            "product_data": {"name": "Platform Fee"},
        },
    })
    
    # Add tax
    if pricing["tax_amount"] > 0:
        line_items.append({
            "quantity": 1,
            "price_data": {
                "currency": "bdt",
                "unit_amount": int(pricing["tax_amount"] * 100),
                "product_data": {"name": "Tax"},
            },
        })
    
    # Create order record
    with Session(engine) as session:
        order = Order(
            buyer_id=current_user.id,
            subtotal=pricing["subtotal"],
            platform_fee=pricing["platform_fee"],
            total=pricing["total"]
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        
        # Add order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )
            session.add(order_item)
        
        session.commit()
    
    # Create Stripe checkout session
    try:
        stripe_session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=f"{request.success_url}?order_id={order.id}&session_id={checkout_session_data['session_id']}",
            cancel_url=f"{request.cancel_url}?order_id={order.id}&session_id={checkout_session_data['session_id']}",
            metadata={
                "order_id": str(order.id),
                "checkout_session_id": checkout_session_data["session_id"]
            },
            customer_email=current_user.email,
            shipping_address_collection={
                "allowed_countries": ["US", "CA"]
            } if not request.shipping_address else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Stripe session: {str(e)}")
    
    # Update order with Stripe session ID
    with Session(engine) as session:
        order = session.get(Order, order.id)
        order.stripe_checkout_session_id = stripe_session.id
        session.add(order)
        session.commit()
    
    return {
        "checkout_url": stripe_session.url,
        "order_id": order.id,
        "checkout_session_id": checkout_session_data["session_id"],
        "expires_at": checkout_session_data["expires_at"]
    }


@router.get("/checkout_session/{session_id}")
def get_checkout_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get checkout session data."""
    session_data = checkout_validator.get_checkout_session(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Checkout session not found or expired")
    
    # Verify user owns this session
    if session_data["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return session_data


@router.post("/checkout_session/{session_id}/validate")
def validate_checkout_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Re-validate checkout session before payment."""
    session_data = checkout_validator.get_checkout_session(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Checkout session not found or expired")
    
    # Verify user owns this session
    if session_data["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Re-validate session
    validation_result = checkout_validator.validate_checkout_session(session_id)
    
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result)
    
    return validation_result["session_data"]


@router.post("/payment_intent")
def create_payment_intent(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Create payment intent for direct payment processing."""
    
    amount = request.get("amount")
    order_id = request.get("order_id")
    
    if not amount:
        raise HTTPException(status_code=400, detail="Amount is required")
    
    try:
        result = payment_service.create_payment_intent(
            amount=amount,
            order_id=order_id,
            customer_email=current_user.email,
            metadata={"user_id": str(current_user.id)}
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment intent: {str(e)}")


@router.get("/payment_intent/{payment_intent_id}")
def get_payment_intent(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retrieve payment intent details."""
    
    try:
        result = payment_service.retrieve_payment_intent(payment_intent_id)
        
        # Verify user has access to this payment intent
        metadata = result.get("metadata", {})
        if metadata.get("user_id") != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payment intent: {str(e)}")


@router.post("/payment_intent/{payment_intent_id}/retry")
def retry_payment(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retry a failed payment."""
    
    try:
        # First verify user has access
        payment_details = payment_service.retrieve_payment_intent(payment_intent_id)
        metadata = payment_details.get("metadata", {})
        if metadata.get("user_id") != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = payment_service.retry_failed_payment(payment_intent_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retry payment: {str(e)}")


@router.post("/refund")
def create_refund(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Create refund for a payment."""
    
    payment_intent_id = request.get("payment_intent_id")
    amount = request.get("amount")  # Optional - full refund if not specified
    reason = request.get("reason")
    
    if not payment_intent_id:
        raise HTTPException(status_code=400, detail="Payment intent ID is required")
    
    try:
        # Verify user has access to this payment
        payment_details = payment_service.retrieve_payment_intent(payment_intent_id)
        metadata = payment_details.get("metadata", {})
        
        # Check if user owns the payment or is admin
        if metadata.get("user_id") != str(current_user.id) and current_user.role.value != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = payment_service.refund_payment(
            payment_intent_id=payment_intent_id,
            amount=amount,
            reason=reason,
            metadata={"refunded_by": str(current_user.id)}
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create refund: {str(e)}")


@router.get("/payment_methods")
def get_supported_payment_methods():
    """Get list of supported payment methods."""
    
    return {
        "payment_methods": [
            {
                "type": "card",
                "name": "Credit/Debit Card",
                "supported_brands": ["visa", "mastercard", "amex", "discover"],
                "enabled": True
            },
            {
                "type": "ach_debit",
                "name": "Bank Transfer (ACH)",
                "description": "Direct bank account transfer",
                "enabled": False  # Enable when ready
            },
            {
                "type": "apple_pay",
                "name": "Apple Pay",
                "description": "Pay with Apple Pay",
                "enabled": False  # Enable when configured
            },
            {
                "type": "google_pay",
                "name": "Google Pay",
                "description": "Pay with Google Pay",
                "enabled": False  # Enable when configured
            }
        ]
    }


@router.post("/stripe_webhook")
async def stripe_webhook(request: Request):
    """Enhanced Stripe webhook handler with comprehensive event processing."""
    raw_body = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    
    try:
        result = payment_service.handle_webhook_event(raw_body, sig_header)
        return {"received": True, "processed": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@router.get("/orders", response_model=List[Order])
def list_my_orders(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        return session.exec(select(Order).where(Order.buyer_id == current_user.id).order_by(Order.created_at.desc())).all()


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


