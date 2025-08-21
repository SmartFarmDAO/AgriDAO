from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from ..database import engine
from ..models import User


router = APIRouter()


@router.get("/", response_model=List[User])
def list_users() -> List[User]:
    with Session(engine) as session:
        return session.exec(select(User)).all()


@router.post("/", response_model=User, status_code=201)
def create_user(user: User) -> User:
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_update: User) -> User:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_update.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()

