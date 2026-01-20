"""
Cart Service for persistent cart storage and management.
Handles cart operations, synchronization, and validation.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlmodel import Session, select
from fastapi import HTTPException

from ..database import engine
from ..models import Cart, CartItem, Product, User, CartStatus
from ..services.redis_service import RedisService


class CartService:
    """Service for managing shopping cart operations."""
    
    def __init__(self):
        self.redis_service = RedisService()
        self.cart_expiry_hours = 24 * 7  # 7 days
    
    def get_or_create_cart(
        self, 
        user_id: Optional[int] = None, 
        session_id: Optional[str] = None
    ) -> Cart:
        """Get existing cart or create new one for user/session."""
        if not user_id and not session_id:
            raise HTTPException(
                status_code=400, 
                detail="Either user_id or session_id must be provided"
            )
        
        with Session(engine) as session:
            # Try to find existing active cart
            query = select(Cart).where(Cart.status == CartStatus.ACTIVE)
            if user_id:
                query = query.where(Cart.user_id == user_id)
            else:
                query = query.where(Cart.session_id == session_id)
            
            cart = session.exec(query).first()
            
            if cart:
                # Check if cart is expired
                if cart.expires_at and cart.expires_at < datetime.utcnow():
                    cart.status = CartStatus.EXPIRED
                    session.add(cart)
                    session.commit()
                    cart = None
            
            if not cart:
                # Create new cart
                expires_at = datetime.utcnow() + timedelta(hours=self.cart_expiry_hours)
                cart = Cart(
                    user_id=user_id,
                    session_id=session_id,
                    expires_at=expires_at
                )
                session.add(cart)
                session.commit()
                session.refresh(cart)
            
            return cart
    
    def add_item(
        self, 
        cart_id: int, 
        product_id: int, 
        quantity: int = 1
    ) -> CartItem:
        """Add item to cart or update quantity if exists."""
        with Session(engine) as session:
            # Validate product exists and is available
            product = session.get(Product, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            if product.quantity_available < quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Only {product.quantity_available} items available"
                )
            
            # Check if item already exists in cart
            existing_item = session.exec(
                select(CartItem).where(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            ).first()
            
            if existing_item:
                # Update quantity
                new_quantity = existing_item.quantity + quantity
                if product.quantity_available < new_quantity:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Only {product.quantity_available} items available"
                    )
                existing_item.quantity = new_quantity
                existing_item.updated_at = datetime.utcnow()
                session.add(existing_item)
                cart_item = existing_item
            else:
                # Create new cart item
                cart_item = CartItem(
                    cart_id=cart_id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price
                )
                session.add(cart_item)
            
            # Update cart timestamp
            cart = session.get(Cart, cart_id)
            if cart:
                cart.updated_at = datetime.utcnow()
                session.add(cart)
            
            session.commit()
            session.refresh(cart_item)
            
            # Invalidate cache
            self._invalidate_cart_cache(cart_id)
            
            return cart_item
    
    def update_item_quantity(
        self, 
        cart_id: int, 
        product_id: int, 
        quantity: int
    ) -> Optional[CartItem]:
        """Update item quantity in cart."""
        if quantity <= 0:
            return self.remove_item(cart_id, product_id)
        
        with Session(engine) as session:
            # Validate product availability
            product = session.get(Product, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            if product.quantity_available < quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Only {product.quantity_available} items available"
                )
            
            cart_item = session.exec(
                select(CartItem).where(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            ).first()
            
            if not cart_item:
                raise HTTPException(status_code=404, detail="Item not found in cart")
            
            cart_item.quantity = quantity
            cart_item.updated_at = datetime.utcnow()
            session.add(cart_item)
            
            # Update cart timestamp
            cart = session.get(Cart, cart_id)
            if cart:
                cart.updated_at = datetime.utcnow()
                session.add(cart)
            
            session.commit()
            session.refresh(cart_item)
            
            # Invalidate cache
            self._invalidate_cart_cache(cart_id)
            
            return cart_item
    
    def remove_item(self, cart_id: int, product_id: int) -> bool:
        """Remove item from cart."""
        with Session(engine) as session:
            cart_item = session.exec(
                select(CartItem).where(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            ).first()
            
            if not cart_item:
                return False
            
            session.delete(cart_item)
            
            # Update cart timestamp
            cart = session.get(Cart, cart_id)
            if cart:
                cart.updated_at = datetime.utcnow()
                session.add(cart)
            
            session.commit()
            
            # Invalidate cache
            self._invalidate_cart_cache(cart_id)
            
            return True
    
    def get_cart_items(self, cart_id: int) -> List[Dict[str, Any]]:
        """Get all items in cart with product details."""
        cache_key = f"cart_items:{cart_id}"
        
        # Try to get from cache first
        cached_items = self.redis_service.get_json(cache_key)
        if cached_items is not None:
            return cached_items
        
        with Session(engine) as session:
            cart_items = session.exec(
                select(CartItem).where(CartItem.cart_id == cart_id)
            ).all()
            
            if not cart_items:
                return []
            
            # Get product details
            product_ids = [item.product_id for item in cart_items]
            products = {
                p.id: p for p in session.exec(
                    select(Product).where(Product.id.in_(product_ids))
                ).all()
            }
            
            items_data = []
            for item in cart_items:
                product = products.get(item.product_id)
                if product:
                    items_data.append({
                        "id": item.id,
                        "product_id": item.product_id,
                        "product_name": product.name,
                        "product_description": product.description,
                        "product_image": product.images[0] if product.images else None,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "total_price": float(item.unit_price * item.quantity),
                        "available_quantity": product.quantity_available,
                        "added_at": item.added_at.isoformat(),
                        "updated_at": item.updated_at.isoformat()
                    })
            
            # Cache for 5 minutes
            self.redis_service.set_json(cache_key, items_data, expire=300)
            
            return items_data
    
    def get_cart_summary(self, cart_id: int) -> Dict[str, Any]:
        """Get cart summary with totals."""
        items = self.get_cart_items(cart_id)
        
        subtotal = sum(item["total_price"] for item in items)
        item_count = sum(item["quantity"] for item in items)
        
        return {
            "cart_id": cart_id,
            "item_count": item_count,
            "subtotal": round(subtotal, 2),
            "items": items
        }
    
    def validate_cart_items(self, cart_id: int) -> Dict[str, Any]:
        """Validate all items in cart against current product availability."""
        with Session(engine) as session:
            cart_items = session.exec(
                select(CartItem).where(CartItem.cart_id == cart_id)
            ).all()
            
            if not cart_items:
                return {"valid": True, "issues": []}
            
            # Get current product data
            product_ids = [item.product_id for item in cart_items]
            products = {
                p.id: p for p in session.exec(
                    select(Product).where(Product.id.in_(product_ids))
                ).all()
            }
            
            issues = []
            valid = True
            
            for item in cart_items:
                product = products.get(item.product_id)
                
                if not product:
                    issues.append({
                        "type": "product_not_found",
                        "product_id": item.product_id,
                        "message": "Product no longer available"
                    })
                    valid = False
                    continue
                
                if product.quantity_available < item.quantity:
                    issues.append({
                        "type": "insufficient_stock",
                        "product_id": item.product_id,
                        "product_name": product.name,
                        "requested_quantity": item.quantity,
                        "available_quantity": product.quantity_available,
                        "message": f"Only {product.quantity_available} items available"
                    })
                    valid = False
                
                # Check if price has changed significantly (more than 10%)
                price_diff = abs(float(product.price - item.unit_price))
                if price_diff > float(item.unit_price) * 0.1:
                    issues.append({
                        "type": "price_changed",
                        "product_id": item.product_id,
                        "product_name": product.name,
                        "old_price": float(item.unit_price),
                        "new_price": float(product.price),
                        "message": f"Price changed from ${item.unit_price} to ${product.price}"
                    })
                    # Price changes don't invalidate cart, just notify
            
            return {"valid": valid, "issues": issues}
    
    def clear_cart(self, cart_id: int) -> bool:
        """Clear all items from cart."""
        with Session(engine) as session:
            cart_items = session.exec(
                select(CartItem).where(CartItem.cart_id == cart_id)
            ).all()
            
            for item in cart_items:
                session.delete(item)
            
            # Update cart timestamp
            cart = session.get(Cart, cart_id)
            if cart:
                cart.updated_at = datetime.utcnow()
                session.add(cart)
            
            session.commit()
            
            # Invalidate cache
            self._invalidate_cart_cache(cart_id)
            
            return True
    
    def merge_carts(self, target_cart_id: int, source_cart_id: int) -> bool:
        """Merge items from source cart into target cart."""
        with Session(engine) as session:
            source_items = session.exec(
                select(CartItem).where(CartItem.cart_id == source_cart_id)
            ).all()
            
            for source_item in source_items:
                # Check if item exists in target cart
                existing_item = session.exec(
                    select(CartItem).where(
                        CartItem.cart_id == target_cart_id,
                        CartItem.product_id == source_item.product_id
                    )
                ).first()
                
                if existing_item:
                    # Update quantity
                    existing_item.quantity += source_item.quantity
                    existing_item.updated_at = datetime.utcnow()
                    session.add(existing_item)
                else:
                    # Create new item in target cart
                    new_item = CartItem(
                        cart_id=target_cart_id,
                        product_id=source_item.product_id,
                        quantity=source_item.quantity,
                        unit_price=source_item.unit_price
                    )
                    session.add(new_item)
                
                # Remove from source cart
                session.delete(source_item)
            
            # Mark source cart as expired
            source_cart = session.get(Cart, source_cart_id)
            if source_cart:
                source_cart.status = CartStatus.EXPIRED
                session.add(source_cart)
            
            # Update target cart timestamp
            target_cart = session.get(Cart, target_cart_id)
            if target_cart:
                target_cart.updated_at = datetime.utcnow()
                session.add(target_cart)
            
            session.commit()
            
            # Invalidate caches
            self._invalidate_cart_cache(target_cart_id)
            self._invalidate_cart_cache(source_cart_id)
            
            return True
    
    def cleanup_expired_carts(self) -> int:
        """Clean up expired carts and return count of cleaned carts."""
        with Session(engine) as session:
            expired_carts = session.exec(
                select(Cart).where(
                    Cart.expires_at < datetime.utcnow(),
                    Cart.status == CartStatus.ACTIVE
                )
            ).all()
            
            count = 0
            for cart in expired_carts:
                # Delete cart items
                cart_items = session.exec(
                    select(CartItem).where(CartItem.cart_id == cart.id)
                ).all()
                
                for item in cart_items:
                    session.delete(item)
                
                # Mark cart as expired
                cart.status = CartStatus.EXPIRED
                session.add(cart)
                count += 1
            
            session.commit()
            return count
    
    def _invalidate_cart_cache(self, cart_id: int) -> None:
        """Invalidate cart cache."""
        cache_key = f"cart_items:{cart_id}"
        try:
            # Use sync delete method if available, otherwise skip cache invalidation
            if hasattr(self.redis_service, 'delete_sync'):
                self.redis_service.delete_sync(cache_key)
            # For now, we'll skip cache invalidation in sync context
            # In production, consider using a background task for cache invalidation
        except Exception:
            # Silently fail cache invalidation - not critical for functionality
            pass