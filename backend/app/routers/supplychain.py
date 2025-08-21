from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from ..database import engine
from ..models import ProvenanceAsset, ProvenanceAssetUpdate


router = APIRouter()


@router.get("/assets", response_model=List[ProvenanceAsset])
def list_assets() -> List[ProvenanceAsset]:
    with Session(engine) as session:
        return session.exec(select(ProvenanceAsset)).all()


@router.post("/assets", response_model=ProvenanceAsset, status_code=201)
def create_asset(asset: ProvenanceAsset) -> ProvenanceAsset:
    with Session(engine) as session:
        session.add(asset)
        session.commit()
        session.refresh(asset)
        return asset


@router.get("/assets/{asset_id}", response_model=ProvenanceAsset)
def get_asset(asset_id: int) -> ProvenanceAsset:
    with Session(engine) as session:
        asset = session.get(ProvenanceAsset, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset


@router.put("/assets/{asset_id}", response_model=ProvenanceAsset)
def update_asset(asset_id: int, asset_update: ProvenanceAssetUpdate) -> ProvenanceAsset:
    with Session(engine) as session:
        asset = session.get(ProvenanceAsset, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        asset_data = asset_update.model_dump(exclude_unset=True)
        for key, value in asset_data.items():
            setattr(asset, key, value)
        
        session.add(asset)
        session.commit()
        session.refresh(asset)
        return asset


@router.delete("/assets/{asset_id}", status_code=204)
def delete_asset(asset_id: int):
    with Session(engine) as session:
        asset = session.get(ProvenanceAsset, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        session.delete(asset)
        session.commit()
        return

