from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel


class Farmer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    quantity: str
    farmer_id: Optional[int] = Field(default=None, foreign_key="farmer.id")
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


class ProvenanceAsset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    origin: Optional[str] = None
    current_location: Optional[str] = None
    qr_code: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ProvenanceAssetUpdate(SQLModel):
    name: Optional[str] = None
    origin: Optional[str] = None
    current_location: Optional[str] = None
    notes: Optional[str] = None


# Commerce models (MVP revenue)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str  # buyer | farmer | admin
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="user.id")
    status: str = "pending"  # pending | confirmed | fulfilled | cancelled
    subtotal: float
    platform_fee: float
    total: float
    payment_status: str = "unpaid"  # unpaid | paid | refunded
    stripe_checkout_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: float
    unit_price: float


class PaymentEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    type: str
    payload: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

