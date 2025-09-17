"""
Enhanced search service for product search and filtering.
"""
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal

from sqlmodel import Session, select, and_, or_, func, text
from fastapi import HTTPException

from ..models import Product, ProductStatus, User
from ..database import engine
from .product_validation import ProductSearchRequest


class SearchService:
    """Service class for enhanced product search and filtering."""

    def __init__(self, session: Session):
        self.session = session

    def search_products(self, search_params: ProductSearchRequest) -> Dict[str, Any]:
        """Enhanced product search with full-text search and advanced filtering."""
        # Build base query
        query = select(Product)
        conditions = []
        
        # Apply status filter (default to active products)
        if search_params.status:
            conditions.append(Product.status == search_params.status)
        else:
            conditions.append(Product.status == ProductStatus.ACTIVE)
        
        # Apply stock filter
        if search_params.in_stock_only:
            conditions.append(Product.quantity_available > 0)
        
        # Apply farmer filter
        if search_params.farmer_id:
            conditions.append(Product.farmer_id == search_params.farmer_id)
        
        # Apply category filter
        if search_params.category:
            conditions.append(Product.category.ilike(f"%{search_params.category}%"))
        
        # Apply price range filters
        if search_params.min_price is not None:
            conditions.append(Product.price >= search_params.min_price)
        
        if search_params.max_price is not None:
            conditions.append(Product.price <= search_params.max_price)
        
        # Apply unit filter
        if search_params.unit:
            conditions.append(Product.unit == search_params.unit)
        
        # Apply tag filters (PostgreSQL JSON operations)
        if search_params.tags:
            tag_conditions = []
            for tag in search_params.tags:
                # Check if the tag exists in the tags JSON array
                tag_conditions.append(
                    func.json_array_length(Product.tags) > 0
                )
                # This is a simplified version - in production, you'd use proper JSON queries
            if tag_conditions:
                conditions.extend(tag_conditions)
        
        # Apply full-text search
        if search_params.query:
            search_conditions = self._build_search_conditions(search_params.query)
            conditions.extend(search_conditions)
        
        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count before pagination
        count_query = select(func.count(Product.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_count = self.session.exec(count_query).one()
        
        # Apply sorting
        query = self._apply_sorting(query, search_params)
        
        # Apply pagination
        query = query.offset(search_params.offset).limit(search_params.limit)
        
        # Execute query
        products = self.session.exec(query).all()
        
        # Enrich results with additional data
        enriched_products = self._enrich_product_results(products, search_params.query)
        
        return {
            "products": enriched_products,
            "total_count": total_count,
            "limit": search_params.limit,
            "offset": search_params.offset,
            "has_more": search_params.offset + len(products) < total_count,
            "filters_applied": self._get_applied_filters(search_params),
            "facets": self._get_search_facets(search_params) if not search_params.query else None
        }

    def _build_search_conditions(self, query_text: str) -> List:
        """Build full-text search conditions."""
        conditions = []
        
        # Split query into terms
        terms = [term.strip() for term in query_text.split() if term.strip()]
        
        for term in terms:
            term_pattern = f"%{term}%"
            
            # Search in multiple fields with different weights
            term_conditions = [
                # High priority: exact name match
                Product.name.ilike(term_pattern),
                # Medium priority: description match
                Product.description.ilike(term_pattern),
                # Lower priority: category match
                Product.category.ilike(term_pattern),
            ]
            
            # Combine term conditions with OR
            conditions.append(or_(*term_conditions))
        
        return conditions

    def _apply_sorting(self, query, search_params: ProductSearchRequest):
        """Apply sorting to the query."""
        sort_column = getattr(Product, search_params.sort_by)
        
        if search_params.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Add secondary sort by ID for consistent pagination
        query = query.order_by(Product.id.asc())
        
        return query

    def _enrich_product_results(self, products: List[Product], search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Enrich product results with additional computed data."""
        enriched = []
        
        for product in products:
            product_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "price": product.price,
                "quantity_available": product.quantity_available,
                "unit": product.unit,
                "farmer_id": product.farmer_id,
                "status": product.status,
                "images": product.images or [],
                "tags": product.tags or [],
                "sku": product.sku,
                "weight": product.weight,
                "dimensions": product.dimensions,
                "min_order_quantity": product.min_order_quantity,
                "max_order_quantity": product.max_order_quantity,
                "harvest_date": product.harvest_date,
                "expiry_date": product.expiry_date,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                
                # Computed fields
                "is_available": product.quantity_available > 0,
                "stock_level": self._get_stock_level(product.quantity_available),
                "price_per_unit": f"{product.price}/{product.unit}",
                "days_until_expiry": self._calculate_days_until_expiry(product.expiry_date),
                
                # Search relevance (if search query provided)
                "relevance_score": self._calculate_relevance_score(product, search_query) if search_query else None
            }
            
            enriched.append(product_dict)
        
        # Sort by relevance if search query provided
        if search_query:
            enriched.sort(key=lambda x: x["relevance_score"] or 0, reverse=True)
        
        return enriched

    def _get_stock_level(self, quantity: int) -> str:
        """Get stock level description."""
        if quantity == 0:
            return "out_of_stock"
        elif quantity <= 5:
            return "low"
        elif quantity <= 20:
            return "medium"
        else:
            return "high"

    def _calculate_days_until_expiry(self, expiry_date) -> Optional[int]:
        """Calculate days until expiry."""
        if not expiry_date:
            return None
        
        from datetime import datetime
        now = datetime.utcnow()
        
        if expiry_date <= now:
            return 0  # Already expired
        
        delta = expiry_date - now
        return delta.days

    def _calculate_relevance_score(self, product: Product, search_query: str) -> float:
        """Calculate search relevance score."""
        if not search_query:
            return 0.0
        
        score = 0.0
        query_lower = search_query.lower()
        
        # Name matches (highest weight)
        if product.name and query_lower in product.name.lower():
            if product.name.lower().startswith(query_lower):
                score += 10.0  # Starts with query
            else:
                score += 5.0   # Contains query
        
        # Description matches (medium weight)
        if product.description and query_lower in product.description.lower():
            score += 2.0
        
        # Category matches (lower weight)
        if product.category and query_lower in product.category.lower():
            score += 1.0
        
        # Tag matches (medium weight)
        if product.tags:
            for tag in product.tags:
                if query_lower in tag.lower():
                    score += 3.0
        
        # Boost score for available products
        if product.quantity_available > 0:
            score *= 1.2
        
        # Boost score for recently updated products
        from datetime import datetime, timedelta
        if product.updated_at and product.updated_at > datetime.utcnow() - timedelta(days=7):
            score *= 1.1
        
        return score

    def _get_applied_filters(self, search_params: ProductSearchRequest) -> Dict[str, Any]:
        """Get summary of applied filters."""
        filters = {}
        
        if search_params.query:
            filters["search_query"] = search_params.query
        
        if search_params.category:
            filters["category"] = search_params.category
        
        if search_params.min_price is not None or search_params.max_price is not None:
            filters["price_range"] = {
                "min": search_params.min_price,
                "max": search_params.max_price
            }
        
        if search_params.tags:
            filters["tags"] = search_params.tags
        
        if search_params.unit:
            filters["unit"] = search_params.unit
        
        if search_params.farmer_id:
            filters["farmer_id"] = search_params.farmer_id
        
        if not search_params.in_stock_only:
            filters["include_out_of_stock"] = True
        
        return filters

    def _get_search_facets(self, search_params: ProductSearchRequest) -> Dict[str, Any]:
        """Get search facets for filtering UI."""
        # Build base conditions (excluding the facet we're calculating)
        base_conditions = [Product.status == ProductStatus.ACTIVE]
        
        if search_params.in_stock_only:
            base_conditions.append(Product.quantity_available > 0)
        
        if search_params.farmer_id:
            base_conditions.append(Product.farmer_id == search_params.farmer_id)
        
        # Get category facets
        category_query = select(Product.category, func.count(Product.id).label('count')).where(
            and_(*base_conditions, Product.category.is_not(None))
        ).group_by(Product.category).order_by(func.count(Product.id).desc())
        
        category_results = self.session.exec(category_query).all()
        categories = [{"value": cat, "count": count} for cat, count in category_results if cat]
        
        # Get unit facets
        unit_query = select(Product.unit, func.count(Product.id).label('count')).where(
            and_(*base_conditions)
        ).group_by(Product.unit).order_by(func.count(Product.id).desc())
        
        unit_results = self.session.exec(unit_query).all()
        units = [{"value": unit, "count": count} for unit, count in unit_results]
        
        # Get price ranges
        price_stats_query = select(
            func.min(Product.price).label('min_price'),
            func.max(Product.price).label('max_price'),
            func.avg(Product.price).label('avg_price')
        ).where(and_(*base_conditions))
        
        price_stats = self.session.exec(price_stats_query).first()
        
        price_ranges = []
        if price_stats and price_stats.min_price and price_stats.max_price:
            min_price = float(price_stats.min_price)
            max_price = float(price_stats.max_price)
            
            # Create price range buckets
            range_size = (max_price - min_price) / 5
            for i in range(5):
                range_min = min_price + (i * range_size)
                range_max = min_price + ((i + 1) * range_size)
                
                count_query = select(func.count(Product.id)).where(
                    and_(
                        *base_conditions,
                        Product.price >= range_min,
                        Product.price < range_max if i < 4 else Product.price <= range_max
                    )
                )
                count = self.session.exec(count_query).one()
                
                if count > 0:
                    price_ranges.append({
                        "min": round(range_min, 2),
                        "max": round(range_max, 2),
                        "count": count
                    })
        
        return {
            "categories": categories,
            "units": units,
            "price_ranges": price_ranges,
            "price_stats": {
                "min": float(price_stats.min_price) if price_stats and price_stats.min_price else 0,
                "max": float(price_stats.max_price) if price_stats and price_stats.max_price else 0,
                "avg": float(price_stats.avg_price) if price_stats and price_stats.avg_price else 0
            } if price_stats else None
        }

    def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query."""
        if not query or len(query) < 2:
            return []
        
        query_pattern = f"%{query}%"
        
        # Get suggestions from product names
        name_query = select(Product.name).where(
            and_(
                Product.name.ilike(query_pattern),
                Product.status == ProductStatus.ACTIVE
            )
        ).distinct().limit(limit)
        
        names = self.session.exec(name_query).all()
        
        # Get suggestions from categories
        category_query = select(Product.category).where(
            and_(
                Product.category.ilike(query_pattern),
                Product.category.is_not(None),
                Product.status == ProductStatus.ACTIVE
            )
        ).distinct().limit(limit)
        
        categories = self.session.exec(category_query).all()
        
        # Combine and deduplicate
        suggestions = list(set(names + categories))
        
        # Sort by relevance (starts with query first)
        query_lower = query.lower()
        suggestions.sort(key=lambda x: (
            not x.lower().startswith(query_lower),  # Starts with query first
            len(x),  # Shorter suggestions first
            x.lower()  # Alphabetical
        ))
        
        return suggestions[:limit]

    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular search terms (placeholder - would need search analytics)."""
        # This would typically come from search analytics data
        # For now, return popular categories
        
        category_query = select(
            Product.category,
            func.count(Product.id).label('product_count')
        ).where(
            and_(
                Product.category.is_not(None),
                Product.status == ProductStatus.ACTIVE
            )
        ).group_by(Product.category).order_by(
            func.count(Product.id).desc()
        ).limit(limit)
        
        results = self.session.exec(category_query).all()
        
        return [
            {
                "term": category,
                "type": "category",
                "product_count": count
            }
            for category, count in results
        ]

    def get_trending_products(self, limit: int = 10) -> List[Product]:
        """Get trending products (recently added or updated)."""
        from datetime import datetime, timedelta
        
        recent_date = datetime.utcnow() - timedelta(days=7)
        
        query = select(Product).where(
            and_(
                Product.status == ProductStatus.ACTIVE,
                Product.quantity_available > 0,
                or_(
                    Product.created_at >= recent_date,
                    Product.updated_at >= recent_date
                )
            )
        ).order_by(Product.updated_at.desc()).limit(limit)
        
        return self.session.exec(query).all()


def get_search_service(session: Session = None) -> SearchService:
    """Dependency to get search service."""
    if session is None:
        session = Session(engine)
    return SearchService(session)