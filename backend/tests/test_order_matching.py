import pytest
from app.services.order_book import OrderBook
from app.models.database import Order, OrderType, OrderStatus

def test_basic_order_matching():
    order_book = OrderBook()
    
    # Create a sell order
    sell_order = Order(
        id=1, type=OrderType.SELL, price=100.0, quantity=10
    )
    
    # Create a buy order that matches
    buy_order = Order(
        id=2, type=OrderType.BUY, price=100.0, quantity=10
    )
    
    # Add sell order first
    trades = order_book.add_order(sell_order)
    assert len(trades) == 0  # No trades yet
    
    # Add buy order - should match
    trades = order_book.add_order(buy_order)
    assert len(trades) == 1
    assert trades[0][2] == 100.0  # Price
    assert trades[0][3] == 10     # Quantity
    
    # Check order status
    assert sell_order.status == OrderStatus.FILLED
    assert buy_order.status == OrderStatus.FILLED

def test_partial_order_matching():
    order_book = OrderBook()
    
    # Create a large sell order
    sell_order = Order(
        id=1, type=OrderType.SELL, price=100.0, quantity=20
    )
    
    # Create a smaller buy order
    buy_order = Order(
        id=2, type=OrderType.BUY, price=100.0, quantity=10
    )
    
    # Add sell order first
    order_book.add_order(sell_order)
    
    # Add buy order - should partially fill
    trades = order_book.add_order(buy_order)
    assert len(trades) == 1
    assert trades[0][3] == 10  # Quantity
    
    # Check order status
    assert sell_order.status == OrderStatus.PARTIALLY_FILLED
    assert sell_order.filled_quantity == 10
    assert buy_order.status == OrderStatus.FILLED