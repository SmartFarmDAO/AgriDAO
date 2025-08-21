from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import engine
from ..models import Product, Farmer, User
from ..deps import get_current_user


router = APIRouter()


@router.get("/products", response_model=List[Product])
def list_products() -> List[Product]:
    with Session(engine) as session:
        return session.exec(select(Product)).all()


@router.post("/products", response_model=Product, status_code=201)
def create_product(
    product: Product,
    current_user: User = Depends(get_current_user),
) -> Product:
    # Only farmers can create products; must have a farmer profile
    if current_user.role != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can create products")

    if not current_user.email:
        raise HTTPException(status_code=400, detail="User has no email on file")

    with Session(engine) as session:
        farmer: Optional[Farmer] = session.exec(
            select(Farmer).where(Farmer.email == current_user.email)
        ).first()
        if not farmer:
            raise HTTPException(status_code=400, detail="Farmer profile not found; please complete onboarding")

        product.farmer_id = farmer.id
        session.add(product)
        session.commit()
        session.refresh(product)
        return product


@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int) -> Product:
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product


