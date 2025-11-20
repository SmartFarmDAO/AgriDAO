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
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
        # Delete related records
        from ..models import UserSession
        sessions = session.exec(select(UserSession).where(UserSession.user_id == user_id)).all()
        for s in sessions:
            session.delete(s)
        
        session.delete(user)
        session.commit()
