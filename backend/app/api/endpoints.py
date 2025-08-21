from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.models.database import Order, Trade, User, OrderType, OrderStatus, get_db
from app.schemas import OrderCreate, OrderResponse, TradeResponse, UserCreate, UserResponse
from app.utils.security import get_current_active_user, get_password_hash, create_access_token
from app.services.order_book import OrderBook

router = APIRouter()
order_book = OrderBook()

# User management endpoints
@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Order endpoints
@router.post("/orders/", response_model=OrderResponse)
def create_order(
    order: OrderCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_order = Order(
        user_id=current_user.id,
        type=order.type,
        price=order.price,
        quantity=order.quantity
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add to order book and execute matching
    executed_trades = order_book.add_order(db_order)
    
    # Save executed trades to database
    for buyer_id, seller_id, price, quantity in executed_trades:
        trade = Trade(
            buyer_order_id=buyer_id,
            seller_order_id=seller_id,
            price=price,
            quantity=quantity,
            user_id=current_user.id
        )
        db.add(trade)
    
    db.commit()
    return db_order

@router.delete("/orders/{order_id}")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot cancel order in current state")
    
    success = order_book.cancel_order(order_id)
    if success:
        order.status = OrderStatus.CANCELLED
        db.commit()
        return {"message": "Order cancelled successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to cancel order")

@router.get("/orders/", response_model=List[OrderResponse])
def get_user_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).offset(skip).limit(limit).all()
    return orders

@router.get("/trades/", response_model=List[TradeResponse])
def get_user_trades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    trades = db.query(Trade).filter(Trade.user_id == current_user.id).offset(skip).limit(limit).all()
    return trades

# WebSocket for real-time updates
@router.websocket("/ws/orderbook")
async def websocket_orderbook(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send order book updates every second
            order_book_data = order_book.get_order_book()
            await websocket.send_json(order_book_data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")