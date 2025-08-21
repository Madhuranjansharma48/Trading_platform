from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    type: str
    price: float
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: str
    filled_quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TradeBase(BaseModel):
    price: float
    quantity: int

class TradeResponse(TradeBase):
    id: int
    buyer_order_id: int
    seller_order_id: int
    executed_at: datetime
    user_id: int

    class Config:
        orm_mode = True