import os
import time
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from ..database import engine
from ..models import User, UserRole
from ..services.auth import token_manager
from ..services.otp_service import otp_service
from ..services.google_oauth import google_oauth_service
from ..deps import get_current_user
from ..middleware.security import get_csrf_middleware


router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    code: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


# Helper functions removed - only OTP authentication is used


@router.post("/otp/request")
def request_otp(payload: OTPRequest):
    """Request OTP via email"""
    result = otp_service.send_otp_email(payload.email)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send OTP"))
    
    # Return appropriate response based on environment
    response = {
        "sent": True,
        "message": result.get("message", "Verification code sent"),
        "expires_in": result.get("expires_in", 300)
    }
    
    # Include dev_code only in development
    if "dev_code" in result:
        response["dev_code"] = result["dev_code"]
    
    return response


@router.post("/otp/verify")
def verify_otp(request: Request, payload: OTPVerify):
    """Verify OTP code"""
    result = otp_service.verify_otp(payload.email, payload.code)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Invalid or expired code"))

    # upsert user
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == payload.email)).first()
        if not user:
            user = User(
                role=UserRole.BUYER, 
                name=payload.email.split("@")[0], 
                email=payload.email,
                email_verified=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            # Mark email as verified
            user.email_verified = True
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # Get user data before session closes
        user_id = user.id
        user_email = user.email
        user_role = user.role
        user_name = user.name
        user_email_verified = user.email_verified
    
    # Create tokens using TokenManager (after session closes, using user data)
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    # Recreate user object with the data (not attached to session)
    user_for_token = User(
        id=user_id,
        email=user_email,
        role=user_role,
        name=user_name,
        email_verified=user_email_verified
    )
    
    return token_manager.create_tokens(user_for_token, user_agent, ip_address)


# OAuth and Magic Link endpoints removed - only email OTP authentication is supported


@router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    result = token_manager.refresh_access_token(payload.refresh_token)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return result


@router.post("/logout")
def logout(request: Request, payload: LogoutRequest, current_user: User = Depends(get_current_user)):
    """Logout user and revoke tokens."""
    # Get access token from header
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        access_token = authorization.split(" ", 1)[1]
        token_manager.revoke_token(access_token)
    
    # Revoke refresh token if provided
    if payload.refresh_token:
        token_manager.revoke_token(payload.refresh_token)
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
def logout_all(current_user: User = Depends(get_current_user)):
    """Logout user from all devices."""
    token_manager.revoke_all_user_sessions(current_user.id)
    return {"message": "Successfully logged out from all devices"}


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role.value,
        "email_verified": current_user.email_verified,
        "phone_verified": current_user.phone_verified,
        "status": current_user.status.value,
        "created_at": current_user.created_at
    }


@router.get("/csrf-token")
def get_csrf_token():
    """Get CSRF token for state-changing operations."""
    csrf_middleware = get_csrf_middleware()
    if csrf_middleware:
        token = csrf_middleware.generate_csrf_token()
        return {"csrf_token": token}
    else:
        raise HTTPException(status_code=500, detail="CSRF protection not available")


@router.get("/google/login")
def google_login(redirect_uri: Optional[str] = None):
    """Initiate Google OAuth login"""
    if not google_oauth_service.enabled:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    auth_url = google_oauth_service.get_authorization_url(redirect_uri)
    return {"authorization_url": auth_url}


@router.get("/google/callback")
async def google_callback(code: str, state: Optional[str] = None):
    """Handle Google OAuth callback"""
    if not google_oauth_service.enabled:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    # Exchange code for user info
    user_info = await google_oauth_service.exchange_code(code)
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to authenticate with Google")
    
    # Get or create user
    with Session(engine) as session:
        email = user_info.get("email")
        name = user_info.get("name", email.split("@")[0])
        picture = user_info.get("picture")
        
        # Check if user exists
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                name=name,
                role=UserRole.BUYER,  # Default role
                email_verified=True,  # Google emails are verified
                status="active"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # Generate tokens
        access_token = token_manager.create_access_token(user)
        refresh_token = token_manager.create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": user.name,
                "email_verified": user.email_verified
            }
        }


class GoogleTokenVerify(BaseModel):
    token: str


@router.post("/google/verify")
async def google_verify_token(payload: GoogleTokenVerify):
    """Verify Google ID token and authenticate user"""
    if not google_oauth_service.enabled:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    # Verify token and get user info
    user_info = await google_oauth_service.verify_token(payload.token)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    # Get or create user
    with Session(engine) as session:
        email = user_info.get("email")
        name = user_info.get("name", email.split("@")[0])
        
        # Check if user exists
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                name=name,
                role=UserRole.BUYER,
                email_verified=True,
                status="active"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # Generate tokens
        access_token = token_manager.create_access_token(user)
        refresh_token = token_manager.create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": user.name,
                "email_verified": user.email_verified
            }
        }


