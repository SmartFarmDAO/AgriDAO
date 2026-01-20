"""
Product service for managing product operations.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException

from ..models import Product, ProductImage, InventoryHistory, ProductStatus, User
from ..database import engine
from .product_validation import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductSearchRequest,
    InventoryUpdateRequest
)


class ProductService:
    """Service class for product management operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_product(self, product_data: ProductCreateRequest, user_id: int) -> Product:
        """Create a new product with validation."""
        # Verify user is a farmer or admin
        user = self.session.get(User, user_id)
        if not user or user.role not in ['farmer', 'admin']:
            raise HTTPException(status_code=403, detail="Only farmers can create products")

        # Check for duplicate SKU if provided
        if product_data.sku:
            existing_sku = self.session.exec(
                select(Product).where(Product.sku == product_data.sku)
            ).first()
            if existing_sku:
                raise HTTPException(status_code=400, detail="SKU already exists")

        # Create product
        product = Product(
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            price=product_data.price,
            quantity_available=product_data.quantity_available,
            unit=product_data.unit,
            farmer_id=product_data.farmer_id or user_id,
            sku=product_data.sku,
            weight=product_data.weight,
            dimensions=product_data.dimensions,
            tags=product_data.tags,
            min_order_quantity=product_data.min_order_quantity,
            max_order_quantity=product_data.max_order_quantity,
            harvest_date=product_data.harvest_date,
            expiry_date=product_data.expiry_date,
            product_metadata=product_data.product_metadata,
            status=ProductStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)

        # Create initial inventory history record
        if product_data.quantity_available > 0:
            self._create_inventory_history(
                product.id,
                "restock",
                product_data.quantity_available,
                0,
                product_data.quantity_available,
                "Initial stock",
                user_id
            )

        return product

    def update_product(self, product_id: int, product_data: ProductUpdateRequest, user_id: int) -> Product:
        """Update an existing product."""
        product = self.session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Verify user owns the product or is admin
        user = self.session.get(User, user_id)
        if not user or (user.role != 'admin' and product.farmer_id != user_id):
            raise HTTPException(status_code=403, detail="Not authorized to update this product")

        # Check for duplicate SKU if being updated
        if product_data.sku and product_data.sku != product.sku:
            existing_sku = self.session.exec(
                select(Product).where(
                    and_(Product.sku == product_data.sku, Product.id != product_id)
                )
            ).first()
            if existing_sku:
                raise HTTPException(status_code=400, detail="SKU already exists")

        # Track quantity changes for inventory history
        old_quantity = product.quantity_available
        
        # Update fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)

        product.updated_at = datetime.utcnow()

        # Auto-update status based on quantity
        if product.quantity_available == 0 and product.status == ProductStatus.ACTIVE:
            product.status = ProductStatus.OUT_OF_STOCK
        elif product.quantity_available > 0 and product.status == ProductStatus.OUT_OF_STOCK:
            product.status = ProductStatus.ACTIVE

        self.session.commit()
        self.session.refresh(product)

        # Create inventory history if quantity changed
        if 'quantity_available' in update_data and product.quantity_available != old_quantity:
            quantity_change = product.quantity_available - old_quantity
            self._create_inventory_history(
                product.id,
                "adjustment",
                quantity_change,
                old_quantity,
                product.quantity_available,
                "Manual adjustment",
                user_id
            )

        return product

    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        return self.session.get(Product, product_id)

    def delete_product(self, product_id: int, user_id: int) -> bool:
        """Soft delete a product by setting status to inactive."""
        product = self.session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Verify user owns the product or is admin
        user = self.session.get(User, user_id)
        if not user or (user.role != 'admin' and product.farmer_id != user_id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this product")

        product.status = ProductStatus.INACTIVE
        product.updated_at = datetime.utcnow()
        
        self.session.commit()
        return True

    def search_products(self, search_params: ProductSearchRequest) -> Dict[str, Any]:
        """Search products with filtering and pagination."""
        query = select(Product)

        # Apply filters
        conditions = []

        if search_params.query:
            # Full-text search on name and description
            search_term = f"%{search_params.query}%"
            conditions.append(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )

        if search_params.category:
            conditions.append(Product.category == search_params.category)

        if search_params.min_price is not None:
            conditions.append(Product.price >= search_params.min_price)

        if search_params.max_price is not None:
            conditions.append(Product.price <= search_params.max_price)

        if search_params.unit:
            conditions.append(Product.unit == search_params.unit)

        if search_params.status:
            conditions.append(Product.status == search_params.status)
        else:
            # Default to active products only
            conditions.append(Product.status == ProductStatus.ACTIVE)

        if search_params.farmer_id:
            conditions.append(Product.farmer_id == search_params.farmer_id)

        if search_params.in_stock_only:
            conditions.append(Product.quantity_available > 0)

        if search_params.tags:
            # PostgreSQL JSON contains operator
            for tag in search_params.tags:
                conditions.append(func.json_array_length(Product.tags) > 0)
                # This would need proper JSON querying in production

        if conditions:
            query = query.where(and_(*conditions))

        # Apply sorting
        sort_column = getattr(Product, search_params.sort_by)
        if search_params.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Get total count
        count_query = select(func.count(Product.id)).where(query.whereclause)
        total_count = self.session.exec(count_query).one()

        # Apply pagination
        query = query.offset(search_params.offset).limit(search_params.limit)

        products = self.session.exec(query).all()

        return {
            "products": products,
            "total_count": total_count,
            "limit": search_params.limit,
            "offset": search_params.offset,
            "has_more": search_params.offset + len(products) < total_count
        }

    def update_inventory(self, product_id: int, inventory_update: InventoryUpdateRequest, user_id: int) -> Product:
        """Update product inventory with history tracking."""
        product = self.session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Verify user owns the product or is admin
        user = self.session.get(User, user_id)
        if not user or (user.role != 'admin' and product.farmer_id != user_id):
            raise HTTPException(status_code=403, detail="Not authorized to update inventory")

        old_quantity = product.quantity_available
        new_quantity = old_quantity + inventory_update.quantity_change

        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Insufficient inventory")

        product.quantity_available = new_quantity
        product.updated_at = datetime.utcnow()

        # Auto-update status based on quantity
        if new_quantity == 0 and product.status == ProductStatus.ACTIVE:
            product.status = ProductStatus.OUT_OF_STOCK
        elif new_quantity > 0 and product.status == ProductStatus.OUT_OF_STOCK:
            product.status = ProductStatus.ACTIVE

        self.session.commit()
        self.session.refresh(product)

        # Create inventory history
        self._create_inventory_history(
            product.id,
            inventory_update.change_type,
            inventory_update.quantity_change,
            old_quantity,
            new_quantity,
            inventory_update.reason,
            user_id,
            inventory_update.reference_id
        )

        return product

    def get_inventory_history(self, product_id: int, limit: int = 50) -> List[InventoryHistory]:
        """Get inventory history for a product."""
        query = select(InventoryHistory).where(
            InventoryHistory.product_id == product_id
        ).order_by(InventoryHistory.created_at.desc()).limit(limit)
        
        return self.session.exec(query).all()

    def get_low_stock_products(self, farmer_id: Optional[int] = None, threshold: int = 10) -> List[Product]:
        """Get products with low stock."""
        query = select(Product).where(
            and_(
                Product.quantity_available <= threshold,
                Product.quantity_available > 0,
                Product.status == ProductStatus.ACTIVE
            )
        )
        
        if farmer_id:
            query = query.where(Product.farmer_id == farmer_id)
        
        return self.session.exec(query).all()

    def get_categories(self) -> List[str]:
        """Get all unique product categories."""
        query = select(Product.category).where(
            and_(
                Product.category.is_not(None),
                Product.status == ProductStatus.ACTIVE
            )
        ).distinct()
        
        categories = self.session.exec(query).all()
        return [cat for cat in categories if cat]

    def _create_inventory_history(
        self,
        product_id: int,
        change_type: str,
        quantity_change: int,
        previous_quantity: int,
        new_quantity: int,
        reason: Optional[str] = None,
        created_by: Optional[int] = None,
        reference_id: Optional[int] = None
    ) -> InventoryHistory:
        """Create an inventory history record."""
        history = InventoryHistory(
            product_id=product_id,
            change_type=change_type,
            quantity_change=quantity_change,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reason=reason,
            created_by=created_by,
            reference_id=reference_id,
            created_at=datetime.utcnow()
        )
        
        self.session.add(history)
        self.session.commit()
        return history


def get_product_service(session: Session = None) -> ProductService:
    """Dependency to get product service."""
    if session is None:
        session = Session(engine)
    return ProductService(session)