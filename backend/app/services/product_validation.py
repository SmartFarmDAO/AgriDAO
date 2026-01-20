"""
Enhanced product validation models and utilities.
"""
import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ProductImageRequest(BaseModel):
    """Product image upload request validation."""
    alt_text: Optional[str] = Field(None, max_length=255)
    sort_order: int = Field(default=0, ge=0)
    is_primary: bool = Field(default=False)


class ProductCreateRequest(BaseModel):
    """Enhanced product creation with comprehensive validation."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    quantity_available: int = Field(..., ge=0)
    unit: str = Field(default="piece", max_length=50)
    farmer_id: Optional[int] = Field(None, gt=0)
    sku: Optional[str] = Field(None, max_length=100)
    weight: Optional[Decimal] = Field(None, gt=0, max_digits=8, decimal_places=2)
    dimensions: Optional[Dict[str, float]] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    min_order_quantity: int = Field(default=1, ge=1)
    max_order_quantity: Optional[int] = Field(None, ge=1)
    harvest_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    product_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v:
            return v.strip()
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v:
            # Allow alphanumeric, spaces, hyphens, underscores
            if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
                raise ValueError('Category contains invalid characters')
            return v.strip()
        return v

    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v):
        if v:
            # SKU should be alphanumeric with hyphens and underscores
            if not re.match(r'^[A-Za-z0-9\-_]+$', v):
                raise ValueError('SKU can only contain letters, numbers, hyphens, and underscores')
        return v

    @field_validator('dimensions')
    @classmethod
    def validate_dimensions(cls, v):
        if v:
            required_keys = {'length', 'width', 'height'}
            if not all(key in v for key in required_keys):
                raise ValueError('Dimensions must include length, width, and height')
            if not all(isinstance(val, (int, float)) and val > 0 for val in v.values()):
                raise ValueError('All dimension values must be positive numbers')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            if len(v) > 20:
                raise ValueError('Maximum 20 tags allowed')
            for tag in v:
                if not isinstance(tag, str) or len(tag.strip()) == 0:
                    raise ValueError('Tags must be non-empty strings')
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
        return [tag.strip().lower() for tag in v] if v else []

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v):
        allowed_units = [
            'piece', 'kg', 'gram', 'pound', 'ounce', 'liter', 'ml',
            'dozen', 'bunch', 'bag', 'box', 'crate', 'basket'
        ]
        if v.lower() not in allowed_units:
            raise ValueError(f'Unit must be one of: {", ".join(allowed_units)}')
        return v.lower()

    def model_post_init(self, __context):
        """Post-init validation for cross-field validation."""
        # Validate max_order_quantity vs min_order_quantity
        if self.max_order_quantity is not None and self.max_order_quantity < self.min_order_quantity:
            raise ValueError('Maximum order quantity must be greater than or equal to minimum order quantity')
        
        # Validate expiry_date vs harvest_date
        if self.expiry_date and self.harvest_date and self.expiry_date <= self.harvest_date:
            raise ValueError('Expiry date must be after harvest date')


class ProductUpdateRequest(BaseModel):
    """Enhanced product update with comprehensive validation."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    quantity_available: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    sku: Optional[str] = Field(None, max_length=100)
    weight: Optional[Decimal] = Field(None, gt=0, max_digits=8, decimal_places=2)
    dimensions: Optional[Dict[str, float]] = None
    tags: Optional[List[str]] = None
    min_order_quantity: Optional[int] = Field(None, ge=1)
    max_order_quantity: Optional[int] = Field(None, ge=1)
    harvest_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    product_metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern=r'^(active|inactive|out_of_stock|draft)$')

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Product name cannot be empty')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            return v.strip()
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
                raise ValueError('Category contains invalid characters')
            return v.strip()
        return v

    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v):
        if v is not None:
            if not re.match(r'^[A-Za-z0-9\-_]+$', v):
                raise ValueError('SKU can only contain letters, numbers, hyphens, and underscores')
        return v

    @field_validator('dimensions')
    @classmethod
    def validate_dimensions(cls, v):
        if v is not None:
            required_keys = {'length', 'width', 'height'}
            if not all(key in v for key in required_keys):
                raise ValueError('Dimensions must include length, width, and height')
            if not all(isinstance(val, (int, float)) and val > 0 for val in v.values()):
                raise ValueError('All dimension values must be positive numbers')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 20:
                raise ValueError('Maximum 20 tags allowed')
            for tag in v:
                if not isinstance(tag, str) or len(tag.strip()) == 0:
                    raise ValueError('Tags must be non-empty strings')
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
            return [tag.strip().lower() for tag in v]
        return v

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v):
        if v is not None:
            allowed_units = [
                'piece', 'kg', 'gram', 'pound', 'ounce', 'liter', 'ml',
                'dozen', 'bunch', 'bag', 'box', 'crate', 'basket'
            ]
            if v.lower() not in allowed_units:
                raise ValueError(f'Unit must be one of: {", ".join(allowed_units)}')
            return v.lower()
        return v

    def model_post_init(self, __context):
        """Post-init validation for cross-field validation."""
        # Validate max_order_quantity vs min_order_quantity
        if (self.max_order_quantity is not None and 
            self.min_order_quantity is not None and 
            self.max_order_quantity < self.min_order_quantity):
            raise ValueError('Maximum order quantity must be greater than or equal to minimum order quantity')
        
        # Validate expiry_date vs harvest_date
        if self.expiry_date and self.harvest_date and self.expiry_date <= self.harvest_date:
            raise ValueError('Expiry date must be after harvest date')


class ProductSearchRequest(BaseModel):
    """Enhanced product search with comprehensive filtering."""
    query: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    unit: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern=r'^(active|inactive|out_of_stock|draft)$')
    farmer_id: Optional[int] = Field(None, gt=0)
    in_stock_only: bool = Field(default=True)
    sort_by: str = Field(default="created_at", pattern=r'^(name|price|created_at|updated_at)$')
    sort_order: str = Field(default="desc", pattern=r'^(asc|desc)$')
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if v:
            return v.strip()
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v:
            return v.strip()
        return v

    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        if v:
            return v.strip()
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v

    def model_post_init(self, __context):
        """Post-init validation for cross-field validation."""
        if (self.max_price is not None and 
            self.min_price is not None and 
            self.max_price < self.min_price):
            raise ValueError('Maximum price must be greater than minimum price')


class InventoryUpdateRequest(BaseModel):
    """Inventory update request validation."""
    quantity_change: int = Field(..., description="Positive for increase, negative for decrease")
    change_type: str = Field(..., pattern=r'^(restock|sale|adjustment|expired|damaged)$')
    reason: Optional[str] = Field(None, max_length=500)
    reference_id: Optional[int] = Field(None, description="Order ID, adjustment ID, etc.")

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if v:
            return v.strip()
        return v


class BulkProductUpdateRequest(BaseModel):
    """Bulk product update request validation."""
    product_ids: List[int] = Field(..., min_length=1, max_length=100)
    updates: ProductUpdateRequest

    @field_validator('product_ids')
    @classmethod
    def validate_product_ids(cls, v):
        if len(set(v)) != len(v):
            raise ValueError('Duplicate product IDs are not allowed')
        return v