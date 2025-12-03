"""
Checkout Service for comprehensive validation and session management.
Handles checkout validation, pricing, tax calculation, and session management.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import re

from sqlmodel import Session, select
from fastapi import HTTPException

from ..database import engine
from ..models import Cart, CartItem, Product, User, Order, OrderItem
from ..services.cart_service import CartService
from ..services.redis_service import RedisService


class CheckoutValidator:
    """Service for validating checkout data and managing checkout sessions."""
    
    def __init__(self):
        self.cart_service = CartService()
        self.redis_service = RedisService()
        self.platform_fee_rate = float(os.getenv("PLATFORM_FEE_RATE", "0.08"))
        self.tax_rate = float(os.getenv("TAX_RATE", "0.0875"))  # Default 8.75%
        self.checkout_session_timeout = 30  # 30 minutes
    
    def validate_inventory(self, cart_id: int) -> Dict[str, Any]:
        """Validate inventory availability for all cart items."""
        validation_result = self.cart_service.validate_cart_items(cart_id)
        
        if not validation_result["valid"]:
            # Filter out only inventory-related issues
            inventory_issues = [
                issue for issue in validation_result["issues"]
                if issue["type"] in ["product_not_found", "insufficient_stock"]
            ]
            
            if inventory_issues:
                return {
                    "valid": False,
                    "error_type": "inventory_validation",
                    "message": "Some items in your cart are no longer available",
                    "issues": inventory_issues
                }
        
        return {"valid": True, "issues": []}
    
    def validate_pricing(self, cart_id: int) -> Dict[str, Any]:
        """Validate pricing and calculate totals."""
        cart_items = self.cart_service.get_cart_items(cart_id)
        
        if not cart_items:
            return {
                "valid": False,
                "error_type": "empty_cart",
                "message": "Cart is empty"
            }
        
        # Validate each item's pricing
        pricing_issues = []
        subtotal = Decimal("0.00")
        
        with Session(engine) as session:
            for item in cart_items:
                product = session.get(Product, item["product_id"])
                if not product:
                    pricing_issues.append({
                        "product_id": item["product_id"],
                        "issue": "Product not found"
                    })
                    continue
                
                current_price = product.price
                cart_price = Decimal(str(item["unit_price"]))
                
                # Allow small price differences (up to 1 cent)
                if abs(current_price - cart_price) > Decimal("0.01"):
                    pricing_issues.append({
                        "product_id": item["product_id"],
                        "product_name": product.name,
                        "cart_price": float(cart_price),
                        "current_price": float(current_price),
                        "issue": "Price has changed"
                    })
                
                # Use current price for calculations
                item_total = current_price * item["quantity"]
                subtotal += item_total
        
        if pricing_issues:
            return {
                "valid": False,
                "error_type": "pricing_validation",
                "message": "Some item prices have changed",
                "issues": pricing_issues
            }
        
        # Calculate fees and taxes
        platform_fee = subtotal * Decimal(str(self.platform_fee_rate))
        tax_amount = subtotal * Decimal(str(self.tax_rate))
        total = subtotal + platform_fee + tax_amount
        
        return {
            "valid": True,
            "pricing": {
                "subtotal": float(subtotal),
                "platform_fee": float(platform_fee),
                "tax_amount": float(tax_amount),
                "total": float(total)
            }
        }
    
    def validate_shipping_address(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """Validate shipping address format and completeness."""
        required_fields = [
            "first_name", "last_name", "address_line_1", 
            "city", "state", "postal_code", "country"
        ]
        
        missing_fields = []
        validation_errors = []
        
        for field in required_fields:
            if not address.get(field) or not str(address[field]).strip():
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "valid": False,
                "error_type": "address_validation",
                "message": "Missing required address fields",
                "missing_fields": missing_fields
            }
        
        # Validate postal code format (basic validation)
        postal_code = str(address["postal_code"]).strip()
        country = str(address["country"]).upper()
        
        if country == "US":
            # US ZIP code validation (5 digits or 5+4 format)
            if not re.match(r'^\d{5}(-\d{4})?$', postal_code):
                validation_errors.append({
                    "field": "postal_code",
                    "message": "Invalid US ZIP code format"
                })
        elif country == "CA":
            # Canadian postal code validation
            if not re.match(r'^[A-Z]\d[A-Z] \d[A-Z]\d$', postal_code.upper()):
                validation_errors.append({
                    "field": "postal_code",
                    "message": "Invalid Canadian postal code format"
                })
        
        # Validate state/province for US/CA
        if country in ["US", "CA"]:
            state = str(address["state"]).strip()
            if len(state) < 2:
                validation_errors.append({
                    "field": "state",
                    "message": "State/province is required"
                })
        
        if validation_errors:
            return {
                "valid": False,
                "error_type": "address_format",
                "message": "Address format validation failed",
                "errors": validation_errors
            }
        
        # Format address consistently
        formatted_address = {
            "first_name": str(address["first_name"]).strip().title(),
            "last_name": str(address["last_name"]).strip().title(),
            "address_line_1": str(address["address_line_1"]).strip(),
            "address_line_2": str(address.get("address_line_2", "")).strip() or None,
            "city": str(address["city"]).strip().title(),
            "state": str(address["state"]).strip().upper(),
            "postal_code": postal_code.upper(),
            "country": country,
            "phone": str(address.get("phone", "")).strip() or None
        }
        
        return {
            "valid": True,
            "formatted_address": formatted_address
        }
    
    def validate_user_eligibility(self, user_id: int) -> Dict[str, Any]:
        """Validate user eligibility for checkout."""
        with Session(engine) as session:
            user = session.get(User, user_id)
            
            if not user:
                return {
                    "valid": False,
                    "error_type": "user_not_found",
                    "message": "User not found"
                }
            
            if user.status.value != "active":
                return {
                    "valid": False,
                    "error_type": "user_inactive",
                    "message": "User account is not active"
                }
            
            # Check for email verification if required
            if not user.email_verified and os.getenv("REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true":
                return {
                    "valid": False,
                    "error_type": "email_not_verified",
                    "message": "Email verification required for checkout"
                }
            
            return {"valid": True, "user": user}
    
    def create_checkout_session(
        self, 
        user_id: int, 
        cart_id: int, 
        shipping_address: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a checkout session with validation and timeout."""
        
        # Validate user eligibility
        user_validation = self.validate_user_eligibility(user_id)
        if not user_validation["valid"]:
            return user_validation
        
        # Validate inventory
        inventory_validation = self.validate_inventory(cart_id)
        if not inventory_validation["valid"]:
            return inventory_validation
        
        # Validate pricing
        pricing_validation = self.validate_pricing(cart_id)
        if not pricing_validation["valid"]:
            return pricing_validation
        
        # Validate shipping address
        address_validation = self.validate_shipping_address(shipping_address)
        if not address_validation["valid"]:
            return address_validation
        
        # Create checkout session
        session_id = f"checkout_{user_id}_{cart_id}_{int(datetime.utcnow().timestamp())}"
        expires_at = datetime.utcnow() + timedelta(minutes=self.checkout_session_timeout)
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "cart_id": cart_id,
            "shipping_address": address_validation["formatted_address"],
            "pricing": pricing_validation["pricing"],
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "status": "active"
        }
        
        # Store session in Redis with expiration
        try:
            cache_key = f"checkout_session:{session_id}"
            self.redis_service.set_json(
                cache_key, 
                session_data, 
                expire=self.checkout_session_timeout * 60
            )
        except Exception:
            # If Redis fails, continue without caching
            pass
        
        return {
            "valid": True,
            "checkout_session": session_data
        }
    
    def get_checkout_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve checkout session data."""
        try:
            cache_key = f"checkout_session:{session_id}"
            session_data = self.redis_service.get_json(cache_key)
            
            if session_data:
                # Check if session is expired
                expires_at = datetime.fromisoformat(session_data["expires_at"])
                if expires_at < datetime.utcnow():
                    self.redis_service.delete(cache_key)
                    return None
                
                return session_data
        except Exception:
            pass
        
        return None
    
    def validate_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """Validate checkout session and re-validate all data."""
        session_data = self.get_checkout_session(session_id)
        
        if not session_data:
            return {
                "valid": False,
                "error_type": "session_expired",
                "message": "Checkout session has expired"
            }
        
        # Re-validate inventory and pricing
        cart_id = session_data["cart_id"]
        
        inventory_validation = self.validate_inventory(cart_id)
        if not inventory_validation["valid"]:
            return inventory_validation
        
        pricing_validation = self.validate_pricing(cart_id)
        if not pricing_validation["valid"]:
            return pricing_validation
        
        # Update session with latest pricing if changed
        if pricing_validation["pricing"] != session_data["pricing"]:
            session_data["pricing"] = pricing_validation["pricing"]
            session_data["updated_at"] = datetime.utcnow().isoformat()
            
            try:
                cache_key = f"checkout_session:{session_id}"
                self.redis_service.set_json(
                    cache_key, 
                    session_data, 
                    expire=self.checkout_session_timeout * 60
                )
            except Exception:
                pass
        
        return {
            "valid": True,
            "session_data": session_data
        }
    
    def invalidate_checkout_session(self, session_id: str) -> bool:
        """Invalidate checkout session."""
        try:
            cache_key = f"checkout_session:{session_id}"
            self.redis_service.delete(cache_key)
            return True
        except Exception:
            return False
    
    def calculate_tax(self, subtotal: Decimal, shipping_address: Dict[str, Any]) -> Decimal:
        """Calculate tax based on shipping address."""
        # Simple tax calculation - in production, integrate with tax service
        state = shipping_address.get("state", "").upper()
        country = shipping_address.get("country", "").upper()
        
        # US state tax rates (simplified)
        us_tax_rates = {
            "CA": 0.0875,  # California
            "NY": 0.08,    # New York
            "TX": 0.0625,  # Texas
            "FL": 0.06,    # Florida
            # Add more states as needed
        }
        
        if country == "US" and state in us_tax_rates:
            tax_rate = Decimal(str(us_tax_rates[state]))
        else:
            # Default tax rate
            tax_rate = Decimal(str(self.tax_rate))
        
        return subtotal * tax_rate
    
    def estimate_shipping(
        self, 
        cart_items: List[Dict[str, Any]], 
        shipping_address: Dict[str, Any]
    ) -> Decimal:
        """Estimate shipping cost based on items and address."""
        # Simple shipping calculation - in production, integrate with shipping service
        total_weight = Decimal("0.0")
        
        with Session(engine) as session:
            for item in cart_items:
                product = session.get(Product, item["product_id"])
                if product and product.weight:
                    item_weight = product.weight * item["quantity"]
                    total_weight += item_weight
        
        # Base shipping rate
        base_rate = Decimal("5.99")
        
        # Weight-based additional cost
        if total_weight > 5:  # Over 5 lbs
            additional_cost = (total_weight - 5) * Decimal("0.50")
            base_rate += additional_cost
        
        # Distance-based adjustment (simplified)
        state = shipping_address.get("state", "").upper()
        if state in ["CA", "OR", "WA"]:  # West Coast
            base_rate += Decimal("2.00")
        elif state in ["NY", "NJ", "CT"]:  # East Coast
            base_rate += Decimal("1.50")
        
        return base_rate