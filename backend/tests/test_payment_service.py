"""
Tests for payment service functionality.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.payment_service import PaymentService


@pytest.fixture
def payment_service():
    """Create payment service instance."""
    return PaymentService()


class TestPaymentService:
    """Test payment service operations."""
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_create, payment_service):
        """Test successful payment intent creation."""
        # Mock Stripe response
        mock_intent = Mock()
        mock_intent.id = "pi_test_123"
        mock_intent.client_secret = "pi_test_123_secret"
        mock_intent.status = "requires_payment_method"
        mock_create.return_value = mock_intent
        
        result = payment_service.create_payment_intent(
            amount=Decimal("10.99"),
            order_id=1,
            customer_email="test@example.com"
        )
        
        assert result["payment_intent_id"] == "pi_test_123"
        assert result["client_secret"] == "pi_test_123_secret"
        assert result["status"] == "requires_payment_method"
        assert result["amount"] == Decimal("10.99")
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_card_declined(self, mock_create, payment_service):
        """Test payment intent creation with card declined."""
        import stripe
        
        # Mock card declined error
        mock_create.side_effect = stripe.error.CardError(
            message="Your card was declined.",
            param="card",
            code="card_declined",
            decline_code="generic_decline"
        )
        
        with pytest.raises(Exception) as exc_info:
            payment_service.create_payment_intent(
                amount=Decimal("10.99"),
                customer_email="test@example.com"
            )
        
        # Should raise HTTPException with card declined details
        assert "card_declined" in str(exc_info.value)
    
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_success(self, mock_create, payment_service):
        """Test successful checkout session creation."""
        # Mock Stripe response
        mock_session = Mock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_123"
        mock_session.payment_status = "unpaid"
        mock_session.expires_at = 1234567890
        mock_create.return_value = mock_session
        
        line_items = [
            {
                "quantity": 1,
                "price_data": {
                    "currency": "usd",
                    "unit_amount": 1099,
                    "product_data": {"name": "Test Product"}
                }
            }
        ]
        
        result = payment_service.create_checkout_session(
            line_items=line_items,
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            order_id=1,
            customer_email="test@example.com"
        )
        
        assert result["checkout_session_id"] == "cs_test_123"
        assert result["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_123"
        assert result["payment_status"] == "unpaid"
    
    @patch('stripe.PaymentIntent.retrieve')
    def test_retrieve_payment_intent_success(self, mock_retrieve, payment_service):
        """Test successful payment intent retrieval."""
        # Mock Stripe response
        mock_intent = Mock()
        mock_intent.id = "pi_test_123"
        mock_intent.status = "succeeded"
        mock_intent.amount = 1099
        mock_intent.currency = "usd"
        mock_intent.metadata = {"order_id": "1"}
        mock_intent.created = 1234567890
        mock_intent.last_payment_error = None
        mock_retrieve.return_value = mock_intent
        
        result = payment_service.retrieve_payment_intent("pi_test_123")
        
        assert result["payment_intent_id"] == "pi_test_123"
        assert result["status"] == "succeeded"
        assert result["amount"] == 10.99  # Converted from cents
        assert result["currency"] == "usd"
    
    @patch('stripe.Refund.create')
    def test_refund_payment_success(self, mock_create, payment_service):
        """Test successful payment refund."""
        # Mock Stripe response
        mock_refund = Mock()
        mock_refund.id = "re_test_123"
        mock_refund.status = "succeeded"
        mock_refund.amount = 1099
        mock_refund.currency = "usd"
        mock_refund.reason = "requested_by_customer"
        mock_refund.created = 1234567890
        mock_create.return_value = mock_refund
        
        result = payment_service.refund_payment(
            payment_intent_id="pi_test_123",
            amount=Decimal("10.99"),
            reason="requested_by_customer"
        )
        
        assert result["refund_id"] == "re_test_123"
        assert result["status"] == "succeeded"
        assert result["amount"] == 10.99
        assert result["reason"] == "requested_by_customer"
    
    def test_handle_webhook_event_invalid_signature(self, payment_service):
        """Test webhook handling with invalid signature."""
        payload = b'{"type": "test.event"}'
        signature = "invalid_signature"
        
        with pytest.raises(Exception):
            payment_service.handle_webhook_event(payload, signature)
    
    @patch('stripe.Webhook.construct_event')
    def test_handle_webhook_event_checkout_completed(self, mock_construct, payment_service):
        """Test webhook handling for checkout completed event."""
        # Mock webhook event
        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "payment_intent": "pi_test_123",
                    "metadata": {"order_id": "1"}
                }
            }
        }
        mock_construct.return_value = mock_event
        
        payload = b'{"type": "checkout.session.completed"}'
        signature = "valid_signature"
        
        with patch.object(payment_service, '_handle_checkout_completed') as mock_handle:
            mock_handle.return_value = {"status": "processed", "order_id": 1}
            
            result = payment_service.handle_webhook_event(payload, signature)
            
            assert result["status"] == "processed"
            mock_handle.assert_called_once()
    
    @patch('stripe.PaymentIntent.create')
    def test_retry_failed_payment_success(self, mock_create, payment_service):
        """Test successful payment retry."""
        # Mock original failed payment intent
        mock_original = Mock()
        mock_original.status = "requires_payment_method"
        mock_original.amount = 1099
        mock_original.currency = "usd"
        mock_original.metadata = {"order_id": "1"}
        
        # Mock new payment intent
        mock_new = Mock()
        mock_new.id = "pi_test_retry_123"
        mock_new.client_secret = "pi_test_retry_123_secret"
        
        with patch('stripe.PaymentIntent.retrieve', return_value=mock_original):
            mock_create.return_value = mock_new
            
            result = payment_service.retry_failed_payment("pi_test_123")
            
            assert result["success"] is True
            assert result["new_payment_intent_id"] == "pi_test_retry_123"
            assert result["client_secret"] == "pi_test_retry_123_secret"
    
    def test_retry_failed_payment_wrong_status(self, payment_service):
        """Test payment retry with wrong status."""
        # Mock payment intent with wrong status
        mock_intent = Mock()
        mock_intent.status = "succeeded"
        
        with patch('stripe.PaymentIntent.retrieve', return_value=mock_intent):
            result = payment_service.retry_failed_payment("pi_test_123")
            
            assert result["success"] is False
            assert "cannot retry" in result["message"]
    
    def test_process_webhook_event_unhandled_type(self, payment_service):
        """Test processing unhandled webhook event type."""
        event = {
            "type": "unknown.event.type",
            "data": {"object": {}}
        }
        
        result = payment_service._process_webhook_event(event)
        
        assert result["status"] == "ignored"
        assert result["event_type"] == "unknown.event.type"