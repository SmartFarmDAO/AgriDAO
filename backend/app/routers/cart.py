"""
Cart API endpoints for shopping cart management.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

from ..services.cart_service import CartService
from ..deps import get_current_user_optional
from ..models import User


router = APIRouter()
cart_service = CartService()


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1


class UpdateCartItemRequest(BaseModel):
    quantity: int


@router.get("/cart")
def get_cart(
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get current cart contents."""
    user_id = current_user.id if current_user else None
    
    if not user_id and not session_id:
        raise HTTPException(
            status_code=400, 
            detail="Either authentication or session ID required"
        )
    
    cart = cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    return cart_service.get_cart_summary(cart.id)


@router.post("/cart/items")
def add_to_cart(
    request: AddToCartRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Add item to cart."""
    user_id = current_user.id if current_user else None
    
    if not user_id and not session_id:
        raise HTTPException(
            status_code=400, 
            detail="Either authentication or session ID required"
        )
    
    cart = cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    cart_item = cart_service.add_item(
        cart_id=cart.id,
        product_id=request.product_id,
        quantity=request.quantity
    )
    
    return {
        "message": "Item added to cart",
        "cart_item_id": cart_item.id,
        "cart_summary": cart_service.get_cart_summary(cart.id)
    }


@router.put("/cart/items/{product_id}")
def update_cart_item(
    product_id: int,
    request: UpdateCartItemRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Update cart item quantity."""
    user_id = current_user.id if current_user else None
    
    if not user_id and not session_id:
        raise HTTPException(
            status_code=400, 
            detail="Either authentication or session ID required"
        )
    
    cart = cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    
    if request.quantity <= 0:
        cart_service.remove_item(cart.id, product_id)
        message = "Item removed from cart"
    else:
        cart_service.update_item_quantity(cart.id, product_id, request.quantity)
        message = "Cart item updated"
    
    return {
        "message": message,
        "cart_summary": cart_service.get_cart_summary(cart.id)
    }


@router.delete("/cart/items/{product_id}")
def remove_from_cart(
    product_id: int,
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Remove item from cart."""
    user_id = current_user.id if current_user else None
    
    if not user_id and not session_id:
        raise HTTPException(
            status_code=400, 
            detail="Either authentication or session ID required"
        )
    
    cart = cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    removed = cart_service.remove_item(cart.id, product_id)
    
    if not removed:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    return {
        "message": "Item removed from cart",
        "cart_summary": cart_service.get_cart_summary(cart.id)
    }


@router.delete("/cart")
def clear_cart(
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Clear all items from cart."""
    user_id = current_user.id if current_user else None
    
    if not user_id and not session_id:
        raise HTTPException(
            status_code=400, 
            detail="Either authentication or session ID required"
        )
    
    cart = cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    cart_service.clear_cart(cart.id)
    
    return {
        "message": "Cart cleared",
        "cart_summary": cart_service.get_cart_summary(cart.id)
    }


@router.get("/cart/validate")
def validate_cart(
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Validate cart items against current product availability."""
    user_id = current_user.id if current_user else None
    
    if not user_id and not session_id:
        raise HTTPException(
            status_code=400, 
            detail="Either authentication or session ID required"
        )
    
    cart = cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    validation_result = cart_service.validate_cart_items(cart.id)
    
    return {
        "cart_id": cart.id,
        "validation": validation_result,
        "cart_summary": cart_service.get_cart_summary(cart.id)
    }


@router.post("/cart/merge")
def merge_carts(
    source_session_id: str,
    current_user: User = Depends(get_current_user_optional)
):
    """Merge anonymous cart into user cart after login."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get user cart
    user_cart = cart_service.get_or_create_cart(user_id=current_user.id)
    
    # Get anonymous cart
    anonymous_cart = cart_service.get_or_create_cart(session_id=source_session_id)
    
    # Merge carts
    cart_service.merge_carts(user_cart.id, anonymous_cart.id)
    
    return {
        "message": "Carts merged successfully",
        "cart_summary": cart_service.get_cart_summary(user_cart.id)
    }