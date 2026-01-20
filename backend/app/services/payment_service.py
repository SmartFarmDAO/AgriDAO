"""
Enhanced Payment Service for Stripe integration.
Handles payment processing, error recovery, and webhook management.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum

import stripe
from sqlmodel import Session, select
from fastapi import HTTPException

from ..database import engine
from ..models import Order, OrderItem, PaymentEvent, User
from ..services.redis_service import RedisService


logger = logging.getLogger(__name__)


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentService:
    """Enhanced service for Stripe payment processing."""
    
    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        stripe.api_key = self.stripe_secret_key or None
        self.redis_service = RedisService()
        
        if not self.stripe_secret_key:
            logger.warning("Stripe secret key not configured")
    
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str = "bdt",
        order_id: Optional[int] = None,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create Stripe payment intent with enhanced error handling."""
        
        if not stripe.api_key:
            raise HTTPException(status_code=500, detail="Payment processing not configured")
        
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)
            
            # Prepare metadata
            payment_metadata = metadata or {}
            if order_id:
                payment_metadata["order_id"] = str(order_id)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=payment_metadata,
                receipt_email=customer_email,
                automatic_payment_methods={
                    "enabled": True,
                },
                # Enable setup for future payments
                setup_future_usage="off_session" if customer_email else None,
            )
            
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": amount,
                "currency": currency
            }
            
        except stripe.error.CardError as e:
            # Card was declined
            logger.error(f"Card declined: {e.user_message}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "card_declined",
                    "message": e.user_message or "Your card was declined",
                    "decline_code": e.decline_code
                }
            )
        
        except stripe.error.RateLimitError as e:
            logger.error(f"Stripe rate limit exceeded: {str(e)}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error_type": "rate_limit",
                    "message": "Too many requests. Please try again later."
                }
            )
        
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Invalid Stripe request: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "invalid_request",
                    "message": "Invalid payment request"
                }
            )
        
        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe authentication error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_type": "authentication_error",
                    "message": "Payment service configuration error"
                }
            )
        
        except stripe.error.APIConnectionError as e:
            logger.error(f"Stripe API connection error: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail={
                    "error_type": "service_unavailable",
                    "message": "Payment service temporarily unavailable"
                }
            )
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_type": "payment_error",
                    "message": "Payment processing error"
                }
            )
        
        except Exception as e:
            logger.error(f"Unexpected payment error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_type": "internal_error",
                    "message": "Internal payment processing error"
                }
            )
    
    def create_checkout_session(
        self,
        line_items: List[Dict[str, Any]],
        success_url: str,
        cancel_url: str,
        order_id: Optional[int] = None,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        payment_method_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create Stripe checkout session with enhanced options."""
        
        if not stripe.api_key:
            raise HTTPException(status_code=500, detail="Payment processing not configured")
        
        try:
            # Prepare metadata
            session_metadata = metadata or {}
            if order_id:
                session_metadata["order_id"] = str(order_id)
            
            # Default payment methods
            if not payment_method_types:
                payment_method_types = ["card"]
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=line_items,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=session_metadata,
                customer_email=customer_email,
                payment_method_types=payment_method_types,
                # Enable additional payment methods
                payment_method_options={
                    "card": {
                        "setup_future_usage": "off_session"
                    }
                },
                # Shipping address collection
                shipping_address_collection={
                    "allowed_countries": ["US", "CA"]
                },
                # Tax calculation (if configured)
                automatic_tax={"enabled": False},  # Set to True if tax calculation is configured
                # Invoice creation
                invoice_creation={"enabled": True},
                # Customer creation
                customer_creation="if_required",
            )
            
            return {
                "checkout_session_id": session.id,
                "checkout_url": session.url,
                "payment_status": session.payment_status,
                "expires_at": session.expires_at
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe checkout session error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_type": "checkout_error",
                    "message": "Failed to create checkout session"
                }
            )
        
        except Exception as e:
            logger.error(f"Unexpected checkout error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error_type": "internal_error",
                    "message": "Internal checkout processing error"
                }
            )
    
    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Retrieve payment intent details."""
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,  # Convert from cents
                "currency": intent.currency,
                "metadata": intent.metadata,
                "created": intent.created,
                "last_payment_error": intent.last_payment_error
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve payment intent: {str(e)}")
            raise HTTPException(
                status_code=404,
                detail="Payment intent not found"
            )
    
    def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Process refund for a payment."""
        
        try:
            refund_data = {
                "payment_intent": payment_intent_id,
                "metadata": metadata or {}
            }
            
            if amount:
                refund_data["amount"] = int(amount * 100)  # Convert to cents
            
            if reason:
                refund_data["reason"] = reason
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                "refund_id": refund.id,
                "status": refund.status,
                "amount": refund.amount / 100,  # Convert from cents
                "currency": refund.currency,
                "reason": refund.reason,
                "created": refund.created
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Refund failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "refund_error",
                    "message": "Failed to process refund"
                }
            )
    
    def handle_webhook_event(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Handle Stripe webhook events with comprehensive processing."""
        
        try:
            # Verify webhook signature
            if self.stripe_webhook_secret:
                event = stripe.Webhook.construct_event(
                    payload, signature, self.stripe_webhook_secret
                )
            else:
                # Fallback for development - parse without verification
                import json
                event = json.loads(payload.decode('utf-8'))
                logger.warning("Webhook signature verification skipped - no secret configured")
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Process the event
        return self._process_webhook_event(event)
    
    def _process_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual webhook events."""
        
        event_type = event["type"]
        data_object = event["data"]["object"]
        
        # Log the event
        with Session(engine) as session:
            order_id = None
            if isinstance(data_object, dict):
                metadata = data_object.get("metadata", {})
                order_id = int(metadata.get("order_id", 0)) if metadata.get("order_id") else None
            
            payment_event = PaymentEvent(
                order_id=order_id or 0,
                type=event_type,
                payload=str(event)
            )
            session.add(payment_event)
            session.commit()
        
        # Handle specific event types
        if event_type == "checkout.session.completed":
            return self._handle_checkout_completed(data_object)
        
        elif event_type == "payment_intent.succeeded":
            return self._handle_payment_succeeded(data_object)
        
        elif event_type == "payment_intent.payment_failed":
            return self._handle_payment_failed(data_object)
        
        elif event_type == "charge.dispute.created":
            return self._handle_dispute_created(data_object)
        
        elif event_type == "invoice.payment_succeeded":
            return self._handle_invoice_payment_succeeded(data_object)
        
        elif event_type == "customer.subscription.created":
            return self._handle_subscription_created(data_object)
        
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}
    
    def _handle_checkout_completed(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle completed checkout session."""
        
        metadata = session_data.get("metadata", {})
        order_id = int(metadata.get("order_id", 0)) if metadata.get("order_id") else None
        
        if not order_id:
            logger.error("No order_id in checkout session metadata")
            return {"status": "error", "message": "No order_id found"}
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return {"status": "error", "message": "Order not found"}
            
            # Update order status
            order.payment_status = "paid"
            order.stripe_payment_intent_id = session_data.get("payment_intent")
            order.status = "confirmed"
            
            session.add(order)
            session.commit()
            
            logger.info(f"Order {order_id} marked as paid")
            
            # Send notifications asynchronously
            try:
                from ..services.notification_service import NotificationService
                notification_service = NotificationService()
                notification_service.send_order_confirmation(order_id)
                notification_service.send_payment_confirmation(order_id, session_data.get("payment_intent", ""))
            except Exception as e:
                logger.error(f"Failed to send notifications for order {order_id}: {str(e)}")
            
            # TODO: Trigger order fulfillment process
            # TODO: Update inventory
            
            return {"status": "processed", "order_id": order_id}
    
    def _handle_payment_succeeded(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment intent."""
        
        metadata = payment_intent.get("metadata", {})
        order_id = int(metadata.get("order_id", 0)) if metadata.get("order_id") else None
        
        if order_id:
            with Session(engine) as session:
                order = session.get(Order, order_id)
                if order and order.payment_status != "paid":
                    order.payment_status = "paid"
                    order.stripe_payment_intent_id = payment_intent["id"]
                    session.add(order)
                    session.commit()
        
        return {"status": "processed", "payment_intent_id": payment_intent["id"]}
    
    def _handle_payment_failed(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment intent."""
        
        metadata = payment_intent.get("metadata", {})
        order_id = int(metadata.get("order_id", 0)) if metadata.get("order_id") else None
        
        if order_id:
            with Session(engine) as session:
                order = session.get(Order, order_id)
                if order:
                    order.payment_status = "failed"
                    order.status = "payment_failed"
                    session.add(order)
                    session.commit()
                    
                    # TODO: Send payment failure notification
                    # TODO: Implement retry mechanism
        
        return {"status": "processed", "payment_intent_id": payment_intent["id"]}
    
    def _handle_dispute_created(self, dispute: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dispute creation."""
        
        charge_id = dispute.get("charge")
        if charge_id:
            # TODO: Implement dispute handling logic
            # TODO: Notify administrators
            # TODO: Gather evidence
            logger.warning(f"Dispute created for charge {charge_id}")
        
        return {"status": "processed", "dispute_id": dispute["id"]}
    
    def _handle_invoice_payment_succeeded(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful invoice payment."""
        
        # TODO: Handle subscription or recurring payment logic
        return {"status": "processed", "invoice_id": invoice["id"]}
    
    def _handle_subscription_created(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription creation."""
        
        # TODO: Handle subscription logic if needed for future features
        return {"status": "processed", "subscription_id": subscription["id"]}
    
    def retry_failed_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Retry a failed payment with recovery mechanisms."""
        
        try:
            # Retrieve the failed payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status != "requires_payment_method":
                return {
                    "success": False,
                    "message": f"Payment intent status is {intent.status}, cannot retry"
                }
            
            # Create a new payment intent with the same details
            new_intent = stripe.PaymentIntent.create(
                amount=intent.amount,
                currency=intent.currency,
                metadata=intent.metadata,
                automatic_payment_methods={
                    "enabled": True,
                },
            )
            
            return {
                "success": True,
                "new_payment_intent_id": new_intent.id,
                "client_secret": new_intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retry payment: {str(e)}")
            return {
                "success": False,
                "message": "Failed to create retry payment"
            }