import os
import time
import hmac
import hashlib
import base64
import secrets
from typing import Dict, Optional

import jwt
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from pydantic import BaseModel
from sqlmodel import Session, select

from ..database import engine
from ..models import User


router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_ALG = "HS256"

# In-memory OTP store for MVP (replace with Redis later)
otp_store: Dict[str, Dict[str, float]] = {}


class OTPRequest(BaseModel):
    email: str


class OTPVerify(BaseModel):
    email: str
    code: str


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
    code = _generate_otp()
    expires_at = time.time() + 300  # 5 minutes
    otp_store[payload.email] = {"code": code, "exp": expires_at}

    # TODO: integrate email/SMS provider; for now return code in response for dev
    return {"sent": True, "dev_code": code}


@router.post("/otp/verify")
def verify_otp(payload: OTPVerify):
    record = otp_store.get(payload.email)
    if not record or record["exp"] < time.time() or record["code"] != payload.code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    # upsert user
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == payload.email)).first()
        if not user:
            user = User(role="buyer", name=payload.email.split("@")[0], email=payload.email)
            session.add(user)
            session.commit()
            session.refresh(user)

    # issue JWT
    now = int(time.time())
    token = jwt.encode({"sub": str(user.id), "role": user.role, "iat": now, "exp": now + 86400}, JWT_SECRET, algorithm=JWT_ALG)
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "role": user.role}}


class MagicRequest(BaseModel):
    email: str
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
def magic_verify(token: str = Query(...)):
    email = _verify_magic(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # upsert user
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            user = User(role="buyer", name=email.split("@")[0], email=email)
            session.add(user)
            session.commit()
            session.refresh(user)

    now = int(time.time())
    jwt_token = jwt.encode({"sub": str(user.id), "role": user.role, "iat": now, "exp": now + 86400}, JWT_SECRET, algorithm=JWT_ALG)
    return {"access_token": jwt_token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "role": user.role}}


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


