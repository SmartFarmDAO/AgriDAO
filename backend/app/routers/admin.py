"""Admin-specific endpoints"""
from typing import List
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from ..database import engine
from ..models import User, UserStatus
from ..deps import get_current_user


router = APIRouter()


class RoleUpdate(BaseModel):
    role: str


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin access"""
    # Handle both enum and string role values
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/users", response_model=List[User])
def list_all_users(current_user: User = Depends(require_admin)) -> List[User]:
    """List all users (admin only)"""
    with Session(engine) as session:
        return session.exec(select(User)).all()


@router.put("/users/{user_id}/role", response_model=User)
def update_user_role(
    user_id: int, 
    role_update: RoleUpdate,
    current_user: User = Depends(require_admin)
) -> User:
    """Update user role (admin only)"""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate role
        valid_roles = ["BUYER", "FARMER", "ADMIN"]
        if role_update.role.upper() not in valid_roles:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        user.role = role_update.role.upper()
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@router.post("/users/{user_id}/suspend", response_model=User)
def suspend_user(
    user_id: int,
    current_user: User = Depends(require_admin)
) -> User:
    """Suspend a user (admin only)"""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot suspend yourself")
        
        user.status = UserStatus.SUSPENDED
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin)
):
    """Delete a user (admin only)"""
    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if user.id == current_user.id:
                raise HTTPException(status_code=400, detail="Cannot delete yourself")
            
            # Import all related models
            from ..models import UserSession, Cart, Notification, Order, Farmer, Product
            
            # Check if user has orders - prevent deletion if they do
            order_count = session.exec(
                select(Order).where(Order.buyer_id == user_id)
            ).all()
            
            if order_count:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot delete user with {len(order_count)} existing orders. Please suspend the user instead."
                )
            
            # Delete related records in correct order (respecting foreign key constraints)
            
            # 1. If user is a farmer, handle farmer-related data
            user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            if user_role.upper() == 'FARMER':
                # Find farmer record by email
                farmer = session.exec(select(Farmer).where(Farmer.email == user.email)).first()
                if farmer:
                    # Check if farmer has products
                    products = session.exec(select(Product).where(Product.farmer_id == farmer.id)).all()
                    if products:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Cannot delete farmer with {len(products)} existing products. Please suspend the user instead."
                        )
                    
                    # Delete farmer record
                    session.delete(farmer)
            
            # 2. Delete user sessions
            sessions = session.exec(select(UserSession).where(UserSession.user_id == user_id)).all()
            for s in sessions:
                session.delete(s)
            
            # 3. Delete notifications (if table exists)
            try:
                notifications = session.exec(select(Notification).where(Notification.user_id == user_id)).all()
                for n in notifications:
                    session.delete(n)
            except Exception:
                pass  # Table might not exist
            
            # 4. Delete carts
            try:
                carts = session.exec(select(Cart).where(Cart.user_id == user_id)).all()
                for c in carts:
                    session.delete(c)
            except Exception:
                pass  # Table might not exist
            
            # Commit deletions
            session.commit()
            
            # Now delete the user
            session.delete(user)
            session.commit()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {str(e)}"
        )
