"""AI-powered product recommendation service."""
from typing import List, Optional
from sqlmodel import Session, select, func
from ..models import Product, Order, OrderItem, User


class RecommendationService:
    """Service for generating product recommendations."""

    def __init__(self, session: Session):
        self.session = session

    def get_recommendations(
        self, user_id: Optional[int] = None, limit: int = 6
    ) -> List[Product]:
        """Get personalized product recommendations."""
        if user_id:
            # Personalized recommendations based on purchase history
            return self._get_personalized_recommendations(user_id, limit)
        else:
            # Popular products for anonymous users
            return self._get_popular_products(limit)

    def _get_personalized_recommendations(
        self, user_id: int, limit: int
    ) -> List[Product]:
        """Get recommendations based on user's purchase history."""
        # Get user's purchased products
        purchased_query = (
            select(OrderItem.product_id)
            .join(Order)
            .where(Order.user_id == user_id)
        )
        purchased_ids = [row[0] for row in self.session.exec(purchased_query).all()]

        if not purchased_ids:
            return self._get_popular_products(limit)

        # Get categories of purchased products
        category_query = (
            select(Product.category)
            .where(Product.id.in_(purchased_ids))
            .distinct()
        )
        categories = [row[0] for row in self.session.exec(category_query).all()]

        # Recommend products from same categories, excluding already purchased
        recommendations_query = (
            select(Product)
            .where(
                Product.category.in_(categories),
                Product.id.not_in(purchased_ids),
                Product.status == "active",
                Product.quantity_available > 0,
            )
            .order_by(func.random())
            .limit(limit)
        )

        recommendations = self.session.exec(recommendations_query).all()

        # Fill remaining slots with popular products if needed
        if len(recommendations) < limit:
            remaining = limit - len(recommendations)
            popular = self._get_popular_products(
                remaining, exclude_ids=[p.id for p in recommendations] + purchased_ids
            )
            recommendations.extend(popular)

        return recommendations[:limit]

    def _get_popular_products(
        self, limit: int, exclude_ids: Optional[List[int]] = None
    ) -> List[Product]:
        """Get most popular products based on order frequency."""
        exclude_ids = exclude_ids or []

        # Get product order counts
        order_counts_query = (
            select(OrderItem.product_id, func.count(OrderItem.id).label("order_count"))
            .group_by(OrderItem.product_id)
            .order_by(func.count(OrderItem.id).desc())
        )
        order_counts = {
            row[0]: row[1] for row in self.session.exec(order_counts_query).all()
        }

        # Get active products
        products_query = select(Product).where(
            Product.status == "active",
            Product.quantity_available > 0,
        )

        if exclude_ids:
            products_query = products_query.where(Product.id.not_in(exclude_ids))

        products = self.session.exec(products_query).all()

        # Sort by order count
        sorted_products = sorted(
            products, key=lambda p: order_counts.get(p.id, 0), reverse=True
        )

        return sorted_products[:limit]

    def get_similar_products(self, product_id: int, limit: int = 4) -> List[Product]:
        """Get products similar to the given product."""
        product = self.session.get(Product, product_id)
        if not product:
            return []

        # Find products in same category
        similar_query = (
            select(Product)
            .where(
                Product.category == product.category,
                Product.id != product_id,
                Product.status == "active",
                Product.quantity_available > 0,
            )
            .order_by(func.random())
            .limit(limit)
        )

        return self.session.exec(similar_query).all()

    def get_trending_products(self, days: int = 7, limit: int = 6) -> List[Product]:
        """Get trending products based on recent orders."""
        from datetime import datetime, timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get products ordered in last N days
        trending_query = (
            select(OrderItem.product_id, func.count(OrderItem.id).label("count"))
            .join(Order)
            .where(Order.created_at >= cutoff_date)
            .group_by(OrderItem.product_id)
            .order_by(func.count(OrderItem.id).desc())
            .limit(limit)
        )

        trending_ids = [row[0] for row in self.session.exec(trending_query).all()]

        if not trending_ids:
            return self._get_popular_products(limit)

        # Get product details
        products_query = select(Product).where(
            Product.id.in_(trending_ids),
            Product.status == "active",
        )

        products = self.session.exec(products_query).all()

        # Sort by trending order
        sorted_products = sorted(
            products, key=lambda p: trending_ids.index(p.id) if p.id in trending_ids else 999
        )

        return sorted_products[:limit]
