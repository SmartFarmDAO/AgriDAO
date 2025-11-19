from typing import List, Optional
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select

from ..database import engine
from ..models import Product, Farmer, User
from ..deps import get_current_user


router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload product image"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Save file
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # Return URL
    file_url = f"/uploads/images/{filename}"
    return {"file_url": file_url}


@router.get("/products", response_model=List[Product])
def list_products() -> List[Product]:
    with Session(engine) as session:
        return session.exec(select(Product)).all()


@router.post("/products", response_model=Product, status_code=201)
def create_product(
    product: Product,
    current_user: User = Depends(get_current_user),
) -> Product:
    # Farmers and admins can create products; buyers cannot
    if current_user.role.upper() not in ["FARMER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Only farmers and admins can create products")

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


