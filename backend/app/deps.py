from typing import Optional

from fastapi import Header, HTTPException, Request
from sqlmodel import Session

from .database import engine
from .models import User, UserStatus
from .services.auth import token_manager


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(default=None)
) -> User:
    """Get current authenticated user with automatic token refresh support."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    
    token = authorization.split(" ", 1)[1]
    payload = token_manager.validate_token(token, "access")
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=403, detail="Account is not active")
        
        return user


def get_current_active_user(
    request: Request,
    authorization: Optional[str] = Header(default=None)
) -> User:
    """Get current user and ensure they are active."""
    return get_current_user(request, authorization)


def get_current_user_optional(
    request: Request,
    authorization: Optional[str] = Header(default=None)
) -> Optional[User]:
    """Get current authenticated user, return None if not authenticated."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    
    try:
        token = authorization.split(" ", 1)[1]
        payload = token_manager.validate_token(token, "access")
        
        if not payload:
            return None
        
        user_id = int(payload.get("sub"))
        
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user or user.status != UserStatus.ACTIVE:
                return None
            
            return user
    except Exception:
        return None


def require_role(required_role: str):
    """Dependency factory for role-based access control."""
    def role_checker(user: User = get_current_user) -> User:
        if user.role.value != required_role:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required role: {required_role}"
            )
        return user
    return role_checker


