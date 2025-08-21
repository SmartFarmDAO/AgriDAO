import os
import time
import hmac
import hashlib
import base64
import secrets
from typing import Dict

import jwt
from fastapi import APIRouter, HTTPException
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


