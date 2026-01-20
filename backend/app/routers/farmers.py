from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import engine
from ..models import Farmer, User
from ..deps import get_current_user


router = APIRouter()


@router.get("/", response_model=List[Farmer])
def list_farmers() -> List[Farmer]:
    with Session(engine) as session:
        return session.exec(select(Farmer)).all()


@router.get("/me", response_model=Farmer)
def get_my_farmer_profile(current_user: User = Depends(get_current_user)) -> Farmer:
    """Return the farmer profile linked to the authenticated user by email.
    For MVP we link via email instead of a foreign key.
    """
    if not current_user.email:
        raise HTTPException(status_code=400, detail="User has no email on file")
    with Session(engine) as session:
        farmer: Optional[Farmer] = session.exec(
            select(Farmer).where(Farmer.email == current_user.email)
        ).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer profile not found")
        return farmer


@router.post("/me", response_model=Farmer, status_code=201)
def create_my_farmer_profile(
    farmer: Farmer,
    current_user: User = Depends(get_current_user),
) -> Farmer:
    """Create or return an existing farmer profile for the authenticated user.
    Idempotent by email linkage (no schema change required).
    """
    if not current_user.email:
        raise HTTPException(status_code=400, detail="User has no email on file")

    with Session(engine) as session:
        existing = session.exec(
            select(Farmer).where(Farmer.email == current_user.email)
        ).first()
        if existing:
            return existing

        # Pre-fill linkage via email; prefer provided fields from payload.
        farmer.email = current_user.email
        if not getattr(farmer, "name", None):
            farmer.name = current_user.name or current_user.email.split("@")[0]
        session.add(farmer)
        session.commit()
        session.refresh(farmer)

        # Promote user role to 'farmer' upon successful onboarding (MVP behavior)
        db_user = session.get(User, current_user.id)
        if db_user and db_user.role.lower() != "farmer":
            db_user.role = "FARMER"
            session.add(db_user)
            session.commit()

        return farmer


@router.post("/", response_model=Farmer, status_code=201)
def register_farmer(
    farmer: Farmer,
    current_user: User = Depends(get_current_user),
) -> Farmer:
    """Create or return an existing farmer profile for the authenticated user.
    Idempotent by email linkage (no schema change required).
    """
    if not current_user.email:
        raise HTTPException(status_code=400, detail="User has no email on file")

    with Session(engine) as session:
        existing = session.exec(
            select(Farmer).where(Farmer.email == current_user.email)
        ).first()
        if existing:
            return existing

        # Pre-fill linkage via email; prefer provided fields from payload.
        farmer.email = current_user.email
        if not getattr(farmer, "name", None):
            farmer.name = current_user.name or current_user.email.split("@")[0]
        session.add(farmer)
        session.commit()
        session.refresh(farmer)

        # Promote user role to 'farmer' upon successful onboarding (MVP behavior)
        db_user = session.get(User, current_user.id)
        if db_user and db_user.role.lower() != "farmer":
            db_user.role = "FARMER"
            session.add(db_user)
            session.commit()

        return farmer


@router.get("/{farmer_id}", response_model=Farmer)
def get_farmer(farmer_id: int) -> Farmer:
    with Session(engine) as session:
        farmer = session.get(Farmer, farmer_id)
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")
        return farmer


