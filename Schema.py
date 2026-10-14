
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    name: str
    email: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


# Product schemas
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    stock: int = 0


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int

    model_config = ConfigDict(from_attributes=True)


# Shopping cart schemas
class CartItemCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


class CartItemOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


# Order item schemas
class OrderItemOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)


# Order schemas
class OrderOut(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: Optional[datetime] = None
    items: List[OrderItemOut] = []

    model_config = ConfigDict(from_attributes=True)
