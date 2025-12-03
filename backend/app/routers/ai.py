from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class AdviceRequest(BaseModel):
    crop: str
    location: str


@router.post("/advice")
def get_advice(req: AdviceRequest):
    # Stubbed logic; integrate with real model/provider later
    tips = [
        f"Monitor soil moisture for {req.crop} and irrigate during early morning.",
        "Check local forecast; apply preventive fungicide before prolonged humidity.",
        "Use integrated pest management; encourage beneficial insects.",
    ]
    return {
        "crop": req.crop,
        "location": req.location,
        "advice": tips,
    }


