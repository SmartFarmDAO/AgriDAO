from datetime import datetime
from typing import Optional, List
from enum import Enum
from decimal import Decimal

from sqlmodel import Field, SQLModel, Column, JSON


class UserRole(str, Enum):
    BUYER = "BUYER"
    FARMER = "FARMER"
    ADMIN = "ADMIN"
    MENTOR = "MENTOR"
    TRADER = "TRADER"
    POLICY_MAKER = "POLICY_MAKER"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DRAFT = "draft"


class Farmer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=100)
    price: Decimal = Field(decimal_places=2, max_digits=10)
    quantity: Optional[str] = Field(default="1 piece", max_length=100)  # Legacy field for display
    quantity_available: int = Field(default=0, ge=0)
    unit: str = Field(default="piece", max_length=50)
    farmer_id: Optional[int] = Field(default=None, foreign_key="farmer.id")
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    images: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    product_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    sku: Optional[str] = Field(default=None, max_length=100, unique=True)
    weight: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)
    dimensions: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tags: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    min_order_quantity: int = Field(default=1, ge=1)
    max_order_quantity: Optional[int] = Field(default=None, ge=1)
    harvest_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    blockchain_hash: Optional[str] = Field(default=None, max_length=100)
    blockchain_verified: bool = Field(default=False)
    traceability_id: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProductImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    image_url: str = Field(max_length=500)
    alt_text: Optional[str] = Field(default=None, max_length=255)
    sort_order: int = Field(default=0)
    is_primary: bool = Field(default=False)
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    file_format: Optional[str] = Field(default=None, max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    change_type: str = Field(max_length=50)  # 'restock', 'sale', 'adjustment', 'expired'
    quantity_change: int
    previous_quantity: int
    new_quantity: int
    reason: Optional[str] = Field(default=None, max_length=500)
    reference_id: Optional[int] = None  # order_id, adjustment_id, etc.
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FundingRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    farmer_name: str
    purpose: str
    amount_needed: float
    amount_raised: float = 0.0
    days_left: int
    category: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Proposal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = "open"  # open, passed, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Post(SQLModel, table=True):
    """Social media post for community sharing."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content: str = Field(max_length=1000)
    image_url: Optional[str] = None
    likes_count: int = Field(default=0)
    comments_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Comment(SQLModel, table=True):
    """Comment on a post."""
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")
    content: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Like(SQLModel, table=True):
    """Like on a post."""
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProvenanceAsset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    origin: Optional[str] = None
    current_location: Optional[str] = None
    qr_code: Optional[str] = None
    notes: Optional[str] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[str] = None
    status: Optional[str] = Field(default="Origin")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ProvenanceAssetUpdate(SQLModel):
    name: Optional[str] = None
    origin: Optional[str] = None
    current_location: Optional[str] = None
    notes: Optional[str] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[str] = None
    status: Optional[str] = None


# Commerce models (MVP revenue)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: UserRole = Field(default=UserRole.BUYER)
    sub_role: Optional[str] = Field(default=None, max_length=100)
    name: str
    email: Optional[str] = Field(default=None, unique=True)
    phone: Optional[str] = None
    email_verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)
    profile_image_url: Optional[str] = None
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    FAILED = "failed"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="user.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    subtotal: Decimal = Field(decimal_places=2, max_digits=10)
    platform_fee: Decimal = Field(decimal_places=2, max_digits=10)
    shipping_fee: Decimal = Field(default=Decimal("0.00"), decimal_places=2, max_digits=10)
    tax_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2, max_digits=10)
    total: Decimal = Field(decimal_places=2, max_digits=10)
    payment_status: PaymentStatus = Field(default=PaymentStatus.UNPAID)
    shipping_address: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tracking_number: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=1000)
    stripe_checkout_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    estimated_delivery_date: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderStatusHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    status: OrderStatus
    previous_status: Optional[OrderStatus] = None
    notes: Optional[str] = Field(default=None, max_length=1000)
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    status_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: Decimal = Field(decimal_places=2, max_digits=10)
    unit_price: Decimal = Field(decimal_places=2, max_digits=10)
    farmer_id: Optional[int] = Field(default=None, foreign_key="farmer.id")
    fulfillment_status: Optional[str] = Field(default="pending", max_length=50)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class PaymentEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    type: str
    payload: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Enhanced Authentication Models

class UserSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    session_token: str = Field(unique=True)
    refresh_token: str = Field(unique=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class TokenBlacklist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token_jti: str = Field(unique=True)  # JWT ID claim
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Cart Models

class CartStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CONVERTED = "converted"  # converted to order


class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    session_id: Optional[str] = Field(default=None, max_length=255)  # For anonymous users
    status: CartStatus = Field(default=CartStatus.ACTIVE)
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="cart.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(decimal_places=2, max_digits=10)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Notification Models

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    type: str = Field(max_length=50)  # notification type
    title: str = Field(max_length=255)
    message: str = Field(max_length=1000)
    notification_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Order Review Models

class OrderReview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    buyer_id: int = Field(foreign_key="user.id")
    rating: int = Field(ge=1, le=5)  # 1-5 star rating
    review_text: Optional[str] = Field(default=None, max_length=2000)
    is_anonymous: bool = Field(default=False)
    is_verified_purchase: bool = Field(default=True)
    helpful_votes: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Dispute Resolution Models

class DisputeStatus(str, Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class DisputeType(str, Enum):
    ORDER_NOT_RECEIVED = "order_not_received"
    ITEM_NOT_AS_DESCRIBED = "item_not_as_described"
    DAMAGED_ITEM = "damaged_item"
    WRONG_ITEM = "wrong_item"
    QUALITY_ISSUE = "quality_issue"
    REFUND_REQUEST = "refund_request"
    OTHER = "other"


class Dispute(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    filed_by: int = Field(foreign_key="user.id")  # User who filed the dispute
    dispute_type: DisputeType
    status: DisputeStatus = Field(default=DisputeStatus.OPEN)
    subject: str = Field(max_length=255)
    description: str = Field(max_length=2000)
    evidence_urls: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    resolution: Optional[str] = Field(default=None, max_length=2000)
    resolved_by: Optional[int] = Field(default=None, foreign_key="user.id")
    resolved_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    priority: int = Field(default=1, ge=1, le=5)  # 1=low, 5=high
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DisputeMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dispute_id: int = Field(foreign_key="dispute.id")
    sender_id: int = Field(foreign_key="user.id")
    message: str = Field(max_length=2000)
    is_internal: bool = Field(default=False)  # Internal admin notes
    attachments: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

