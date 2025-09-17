import re
import html
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator, EmailStr
from fastapi import HTTPException


class ValidationError(HTTPException):
    """Custom validation error with user-friendly messages."""
    
    def __init__(self, field: str, message: str, status_code: int = 400):
        detail = {
            "error": "validation_error",
            "field": field,
            "message": message
        }
        super().__init__(status_code=status_code, detail=detail)


def sanitize_html(value: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    if not value:
        return value
    
    # HTML escape the content
    sanitized = html.escape(value)
    
    # Remove any remaining script tags or javascript
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()


def validate_phone_number(phone: str) -> str:
    """Validate and normalize phone number."""
    if not phone:
        return phone
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    if len(digits_only) < 10 or len(digits_only) > 15:
        raise ValidationError("phone", "Phone number must be between 10 and 15 digits")
    
    return digits_only


def validate_password_strength(password: str) -> str:
    """Validate password strength."""
    if len(password) < 8:
        raise ValidationError("password", "Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("password", "Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("password", "Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValidationError("password", "Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("password", "Password must contain at least one special character")
    
    return password


# Enhanced Pydantic Models with Validation

class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="Valid email address")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(default="buyer", pattern=r'^(buyer|farmer|admin)$', description="User role")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValidationError("name", "Name cannot be empty")
        return sanitize_html(v.strip())
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            return validate_phone_number(v)
        return v


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = None
    profile_image_url: Optional[str] = Field(None, max_length=500)
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValidationError("name", "Name cannot be empty")
            return sanitize_html(v.strip())
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            return validate_phone_number(v)
        return v
    
    @validator('profile_image_url')
    def validate_image_url(cls, v):
        if v and not re.match(r'^https?://', v):
            raise ValidationError("profile_image_url", "Profile image URL must be a valid HTTP/HTTPS URL")
        return v


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    category: str = Field(..., pattern=r'^[a-zA-Z0-9\s\-_]+$', max_length=100, description="Product category")
    price: float = Field(..., gt=0, le=1000000, description="Product price")
    quantity: str = Field(..., min_length=1, max_length=50, description="Quantity description")
    farmer_id: Optional[int] = Field(None, description="Farmer ID")
    
    @validator('name')
    def validate_name(cls, v):
        return sanitize_html(v.strip())
    
    @validator('description')
    def validate_description(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v
    
    @validator('category')
    def validate_category(cls, v):
        return sanitize_html(v.strip())
    
    @validator('quantity')
    def validate_quantity(cls, v):
        return sanitize_html(v.strip())


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9\s\-_]+$', max_length=100)
    price: Optional[float] = Field(None, gt=0, le=1000000)
    quantity: Optional[str] = Field(None, min_length=1, max_length=50)
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            return sanitize_html(v.strip())
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return sanitize_html(v.strip())
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            return sanitize_html(v.strip())
        return v
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v is not None:
            return sanitize_html(v.strip())
        return v


class OrderCreateRequest(BaseModel):
    items: List[Dict[str, Any]] = Field(..., min_items=1, description="Order items")
    shipping_address: Dict[str, str] = Field(..., description="Shipping address")
    
    @validator('items')
    def validate_items(cls, v):
        for item in v:
            if 'product_id' not in item or 'quantity' not in item:
                raise ValidationError("items", "Each item must have product_id and quantity")
            
            if not isinstance(item['product_id'], int) or item['product_id'] <= 0:
                raise ValidationError("items", "Product ID must be a positive integer")
            
            if not isinstance(item['quantity'], (int, float)) or item['quantity'] <= 0:
                raise ValidationError("items", "Quantity must be a positive number")
        
        return v
    
    @validator('shipping_address')
    def validate_shipping_address(cls, v):
        required_fields = ['street', 'city', 'state', 'zip_code', 'country']
        for field in required_fields:
            if field not in v or not v[field].strip():
                raise ValidationError("shipping_address", f"Shipping address must include {field}")
            v[field] = sanitize_html(v[field].strip())
        
        # Validate zip code format (basic validation)
        if not re.match(r'^\d{5}(-\d{4})?$', v['zip_code']):
            raise ValidationError("shipping_address", "Invalid zip code format")
        
        return v


class FarmerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    location: Optional[str] = Field(None, max_length=255)
    
    @validator('name')
    def validate_name(cls, v):
        return sanitize_html(v.strip())
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            return validate_phone_number(v)
        return v
    
    @validator('location')
    def validate_location(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v


class ProposalCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    
    @validator('title')
    def validate_title(cls, v):
        return sanitize_html(v.strip())
    
    @validator('description')
    def validate_description(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v


class FundingRequestCreateRequest(BaseModel):
    farmer_name: str = Field(..., min_length=1, max_length=255)
    purpose: str = Field(..., min_length=1, max_length=500)
    amount_needed: float = Field(..., gt=0, le=10000000)
    days_left: int = Field(..., ge=1, le=365)
    category: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    
    @validator('farmer_name')
    def validate_farmer_name(cls, v):
        return sanitize_html(v.strip())
    
    @validator('purpose')
    def validate_purpose(cls, v):
        return sanitize_html(v.strip())
    
    @validator('category')
    def validate_category(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v
    
    @validator('location')
    def validate_location(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v


# Search and Filter Models

class ProductSearchRequest(BaseModel):
    query: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    
    @validator('query')
    def validate_query(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v
    
    @validator('location')
    def validate_location(cls, v):
        if v:
            return sanitize_html(v.strip())
        return v
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValidationError("max_price", "Maximum price must be greater than minimum price")
        return v