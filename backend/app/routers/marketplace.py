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
    if current_user.role.upper() not in ["FARMER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Only farmers and admins can create products")

    if not current_user.email:
        raise HTTPException(status_code=400, detail="User has no email on file")

    with Session(engine) as session:
        # For admins, use provided farmer_id or find first farmer
        if current_user.role.upper() == "ADMIN":
            if not product.farmer_id:
                first_farmer = session.exec(select(Farmer)).first()
                if not first_farmer:
                    raise HTTPException(status_code=400, detail="No farmers in system")
                product.farmer_id = first_farmer.id
        else:
            # For farmers, find their profile
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


@router.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_update: Product,
    current_user: User = Depends(get_current_user),
) -> Product:
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if user owns this product
        if current_user.role.upper() not in ["ADMIN"]:
            farmer = session.exec(
                select(Farmer).where(Farmer.email == current_user.email)
            ).first()
            if not farmer or product.farmer_id != farmer.id:
                raise HTTPException(status_code=403, detail="Not authorized to update this product")
        
        # Update fields
        for key, value in product_update.dict(exclude_unset=True).items():
            if key != "id" and key != "farmer_id":
                setattr(product, key, value)
        
        session.add(product)
        session.commit()
        session.refresh(product)
        return product


@router.patch("/products/{product_id}/status")
def update_product_status(
    product_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if user owns this product or is admin
        if current_user.role.upper() not in ["ADMIN"]:
            farmer = session.exec(
                select(Farmer).where(Farmer.email == current_user.email)
            ).first()
            if not farmer or product.farmer_id != farmer.id:
                raise HTTPException(status_code=403, detail="Not authorized to update this product")
        
        # Validate and set status
        valid_statuses = ["ACTIVE", "INACTIVE", "active", "inactive"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        product.status = status.upper()
        session.add(product)
        session.commit()
        session.refresh(product)
        return {"message": "Product status updated successfully", "product": product}


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if user owns this product
        if current_user.role.upper() not in ["ADMIN"]:
            farmer = session.exec(
                select(Farmer).where(Farmer.email == current_user.email)
            ).first()
            if not farmer or product.farmer_id != farmer.id:
                raise HTTPException(status_code=403, detail="Not authorized to delete this product")
        
        session.delete(product)
        session.commit()
        return {"message": "Product deleted successfully"}


