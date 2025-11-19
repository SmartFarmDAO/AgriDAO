import os
import time
import hmac
import hashlib
import base64
import secrets
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from ..database import engine
from ..models import User, UserRole
from ..services.auth import token_manager
from ..services.otp_service import otp_service
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


def _generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def _sign_magic(email: str, exp: int) -> str:
    payload = f"{email}|{exp}".encode()
    sig = hmac.new(JWT_SECRET.encode(), payload, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(payload + b"|" + base64.urlsafe_b64encode(sig)).decode().rstrip("=")
    return token


def _verify_magic(token: str) -> Optional[str]:
    try:
        # add padding for base64
        padding = '=' * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(token + padding)
        parts = raw.split(b"|")
        if len(parts) != 3:
            return None
        email = parts[0].decode()
        exp = int(parts[1].decode())
        sig = base64.urlsafe_b64decode(parts[2])
        expected = hmac.new(JWT_SECRET.encode(), f"{email}|{exp}".encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return None
        if time.time() > exp:
            return None
        return email
    except Exception:
        return None


@router.post("/otp/request")
def request_otp(payload: OTPRequest):
    """Request OTP via email"""
    result = otp_service.send_otp_email(payload.email)
    
    if result["success"]:
        return {
            "sent": True,
            "expires_in": result["expires_in"]
        }
    else:
        # Fallback for development
        code = otp_service.generate_otp()
        otp_service.otp_store[payload.email] = {
            "code": code,
            "exp": time.time() + 300,
            "attempts": 0
        }
        return {"sent": True, "dev_code": code}


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
        
        # Create tokens using TokenManager (inside session to avoid detached instance)
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None
        
        return token_manager.create_tokens(user, user_agent, ip_address)


class MagicRequest(BaseModel):
    email: EmailStr
    channel: str = "email"  # 'email' or 'whatsapp'


@router.post("/magic/request")
def magic_request(payload: MagicRequest):
    exp = int(time.time()) + 15 * 60
    token = _sign_magic(payload.email, exp)
    verify_url = f"/auth/magic/verify?token={token}"
    # TODO: integrate email/SMS provider (SendGrid, SES, Twilio/WhatsApp) to send verify_url
    # For development, return link in response
    return {"sent": True, "dev_link": verify_url, "expires_in": 900}


@router.get("/magic/verify")
def magic_verify(request: Request, token: str = Query(...)):
    email = _verify_magic(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # upsert user
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            user = User(
                role=UserRole.BUYER, 
                name=email.split("@")[0], 
                email=email,
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

    # Create tokens using TokenManager
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    return token_manager.create_tokens(user, user_agent, ip_address)


@router.get("/oauth/{provider}/start")
def oauth_start(provider: str):
    provider = provider.lower()
    state = secrets.token_urlsafe(24)

    if provider == "google":
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        if not client_id or not redirect_uri:
            raise HTTPException(status_code=400, detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI.")
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
            "state": state,
        }
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return RedirectResponse(url)

    elif provider == "github":
        client_id = os.getenv("GITHUB_CLIENT_ID")
        redirect_uri = os.getenv("GITHUB_REDIRECT_URI")
        if not client_id or not redirect_uri:
            raise HTTPException(status_code=400, detail="GitHub OAuth not configured. Set GITHUB_CLIENT_ID and GITHUB_REDIRECT_URI.")
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "allow_signup": "true",
            "state": state,
        }
        url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
        return RedirectResponse(url)

    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")


@router.get("/oauth/{provider}/callback")
def oauth_callback(provider: str, code: str = Query(...), state: Optional[str] = Query(None)):
    # TODO: Validate state using server-side session or store; omitted for MVP.
    # For now, indicate that the token exchange step is pending implementation.
    raise HTTPException(status_code=501, detail="OAuth callback not implemented yet. I will exchange the code for tokens next.")


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


