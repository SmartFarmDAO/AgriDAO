from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from ..database import engine
from ..models import FundingRequest, Order
from ..services.notification_service import NotificationService


router = APIRouter()


@router.get("/requests", response_model=List[FundingRequest])
def list_requests() -> List[FundingRequest]:
    with Session(engine) as session:
        return session.exec(select(FundingRequest)).all()


@router.post("/requests", response_model=FundingRequest, status_code=201)
def create_request(request: FundingRequest) -> FundingRequest:
    with Session(engine) as session:
        session.add(request)
        session.commit()
        session.refresh(request)
        return request


class DonatePayload(BaseModel):
    amount: float


@router.post("/requests/{request_id}/donate", response_model=FundingRequest)
async def donate(request_id: int, payload: DonatePayload) -> FundingRequest:
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    with Session(engine) as session:
        fr = session.get(FundingRequest, request_id)
        if not fr:
            raise HTTPException(status_code=404, detail="Funding request not found")
        
        previous_raised = fr.amount_raised
        fr.amount_raised += payload.amount
        
        # Check for milestone notifications
        notification_service = NotificationService()
        progress_percentage = (fr.amount_raised / fr.amount_needed) * 100
        previous_percentage = (previous_raised / fr.amount_needed) * 100
        
        # Notify at 25%, 50%, 75%, and 100% milestones
        milestones = [25, 50, 75, 100]
        for milestone in milestones:
            if previous_percentage < milestone <= progress_percentage:
                if milestone == 100:
                    fr.status = "Funded"
                    await notification_service.send_notification(
                        user_id=0,  # Should be farmer's user_id
                        title="🎉 Funding Goal Reached!",
                        message=f"Your funding request '{fr.purpose}' has been fully funded! ${fr.amount_raised} raised.",
                        notification_type="funding_complete"
                    )
                else:
                    await notification_service.send_notification(
                        user_id=0,  # Should be farmer's user_id
                        title=f"📈 {milestone}% Funded!",
                        message=f"Your funding request '{fr.purpose}' is {milestone}% funded. ${fr.amount_raised} of ${fr.amount_needed} raised.",
                        notification_type="funding_milestone"
                    )
        
        session.add(fr)
        session.commit()
        session.refresh(fr)
        return fr


class FinanceMetrics(BaseModel):
    gmv: float
    fee_revenue: float
    orders_total: int
    orders_paid: int
    take_rate: float


@router.get("/metrics", response_model=FinanceMetrics)
def get_metrics() -> FinanceMetrics:
    """Aggregate commerce KPIs for the dashboard.
    GMV and fees are computed from paid orders only for revenue accuracy.
    """
    with Session(engine) as session:
        orders_paid = session.exec(select(Order).where(Order.payment_status == "paid")).all()
        orders_all = session.exec(select(Order)).all()
        gmv = round(sum(o.total for o in orders_paid), 2) if orders_paid else 0.0
        fee_revenue = round(sum(o.platform_fee for o in orders_paid), 2) if orders_paid else 0.0
        take_rate = round((fee_revenue / gmv), 4) if gmv > 0 else 0.0
        return FinanceMetrics(
            gmv=gmv,
            fee_revenue=fee_revenue,
            orders_total=len(orders_all),
            orders_paid=len(orders_paid),
            take_rate=take_rate,
        )


