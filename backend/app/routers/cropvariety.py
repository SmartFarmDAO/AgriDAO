from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.cropvariety import CropVariety
from pydantic import BaseModel

router = APIRouter()

class CropVarietyCreate(BaseModel):
    name: str
    description: str

class CropVarietyResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: str

@router.post("/create_cropvariety", response_model=CropVarietyResponse)
async def create_cropvariety(crop: CropVarietyCreate, db: Session = Depends(get_db)):
    """Generated endpoint for create_cropvariety"""
    db_crop = CropVariety(name=crop.name, description=crop.description)
    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)
    return db_crop

@router.get("/cropvarieties", response_model=List[CropVarietyResponse])
async def get_cropvarieties(db: Session = Depends(get_db)):
    """Get all crop varieties"""
    return db.query(CropVariety).all()
