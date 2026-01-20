"""Recommendations API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import engine
from ..models import Product
from ..services.recommendation_service import RecommendationService


router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


@router.get("/for-you", response_model=List[Product])
def get_recommendations_for_user(
    user_id: Optional[int] = None,
    limit: int = 6,
    session: Session = Depends(get_session),
) -> List[Product]:
    """Get personalized recommendations for a user."""
    service = RecommendationService(session)
    return service.get_recommendations(user_id, limit)


@router.get("/similar/{product_id}", response_model=List[Product])
def get_similar_products(
    product_id: int,
    limit: int = 4,
    session: Session = Depends(get_session),
) -> List[Product]:
    """Get products similar to the given product."""
    service = RecommendationService(session)
    return service.get_similar_products(product_id, limit)


@router.get("/trending", response_model=List[Product])
def get_trending_products(
    days: int = 7,
    limit: int = 6,
    session: Session = Depends(get_session),
) -> List[Product]:
    """Get trending products based on recent orders."""
    service = RecommendationService(session)
    return service.get_trending_products(days, limit)


@router.get("/popular", response_model=List[Product])
def get_popular_products(
    limit: int = 6,
    session: Session = Depends(get_session),
) -> List[Product]:
    """Get most popular products."""
    service = RecommendationService(session)
    return service._get_popular_products(limit)
