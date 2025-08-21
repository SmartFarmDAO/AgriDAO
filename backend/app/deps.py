import os
from typing import Optional

import jwt
from fastapi import Header, HTTPException
from sqlmodel import Session

from .database import engine
from .models import User


def get_current_user(authorization: Optional[str] = Header(default=None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        claims = jwt.decode(token, os.getenv("JWT_SECRET", "devsecret"), algorithms=["HS256"])
        user_id = int(claims.get("sub"))
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid token")

    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


