from typing import List
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, func

from ..database import engine
from ..models import User, UserStatus, Order
from ..deps import get_current_user


router = APIRouter()


class RoleUpdate(BaseModel):
    role: str


class StatusUpdate(BaseModel):
    status: str


@router.get("/", response_model=List[User])
def list_users(current_user: User = Depends(get_current_user)) -> List[User]:
    """List all users (admin only)"""
    # Handle both enum and string role values
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        return session.exec(select(User)).all()


@router.put("/{user_id}/role", response_model=User)
def update_user_role(
    user_id: int, 
    role_update: RoleUpdate,
    current_user: User = Depends(get_current_user)
) -> User:
    """Update user role (admin only)"""
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
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


@router.post("/{user_id}/suspend", response_model=User)
def suspend_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """Suspend a user (admin only)"""
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
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


@router.post("/{user_id}/activate", response_model=User)
def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """Activate a suspended user (admin only)"""
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.status = UserStatus.ACTIVE
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, current_user: User = Depends(get_current_user)) -> User:
    """Get user by ID"""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Users can only view their own profile unless they're admin
        role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        if user.id != current_user.id and role_str.upper() != "ADMIN":
            raise HTTPException(status_code=403, detail="Access denied")
        
        return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    """Delete a user (admin only)"""
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
        # Delete related records to avoid foreign key constraints
        from ..models import UserSession
        from sqlmodel import select
        
        # Delete user sessions
        sessions = session.exec(select(UserSession).where(UserSession.user_id == user_id)).all()
        for s in sessions:
            session.delete(s)
        
        # Check if user has orders - prevent deletion if they do
        order_count = session.exec(
            select(func.count()).select_from(Order).where(Order.buyer_id == user_id)
        ).one()
        
        if order_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete user with {order_count} existing orders. Please archive the user instead."
            )
        
        session.delete(user)
        session.commit()

