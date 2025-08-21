import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import Generator
from sqlalchemy.sql import func
import enum

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///:memory:"
)

# Create engine lazily using DATABASE_URL environment variable. Default to in-memory SQLite
# to make tests and local runs simple and avoid requiring psycopg2 unless a real Postgres URL is set.
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Yield a SQLAlchemy session and ensure it's closed after use.

    This is the dependency used by FastAPI endpoints (Depends(get_db)).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()

class OrderType(enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(enum.Enum):
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    orders = relationship("Order", back_populates="user")
    trades = relationship("Trade", back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(OrderType))
    price = Column(Float)
    quantity = Column(Integer)
    filled_quantity = Column(Integer, default=0)
    status = Column(Enum(OrderStatus), default=OrderStatus.OPEN)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    buyer_order_id = Column(Integer, ForeignKey("orders.id"))
    seller_order_id = Column(Integer, ForeignKey("orders.id"))
    price = Column(Float)
    quantity = Column(Integer)
    executed_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="trades")
    buyer_order = relationship("Order", foreign_keys=[buyer_order_id])
    seller_order = relationship("Order", foreign_keys=[seller_order_id])