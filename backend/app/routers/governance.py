from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from ..database import engine
from ..models import Proposal


router = APIRouter()


@router.get("/proposals", response_model=List[Proposal])
def list_proposals() -> List[Proposal]:
    with Session(engine) as session:
        return session.exec(select(Proposal)).all()


@router.post("/proposals", response_model=Proposal, status_code=201)
def create_proposal(proposal: Proposal) -> Proposal:
    with Session(engine) as session:
        session.add(proposal)
        session.commit()
        session.refresh(proposal)
        return proposal


@router.post("/proposals/{proposal_id}/close", response_model=Proposal)
def close_proposal(proposal_id: int, outcome: str = "passed") -> Proposal:
    if outcome not in ("passed", "rejected"):
        raise HTTPException(status_code=400, detail="Outcome must be 'passed' or 'rejected'")
    with Session(engine) as session:
        prop = session.get(Proposal, proposal_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Proposal not found")
        prop.status = outcome
        session.add(prop)
        session.commit()
        session.refresh(prop)
        return prop


