import heapq
from collections import defaultdict
from typing import List, Dict, Tuple, Any
from app.models.database import Order, OrderType, OrderStatus

class OrderBook:
    def __init__(self):
        # Use heaps for efficient order matching
        self.buy_orders = []  # Max-heap for buys (using negative prices)
        self.sell_orders = []  # Min-heap for sells
        self.orders = {}  # OrderID -> Order mapping
        
    def add_order(self, order: Any) -> List[Tuple]:
        """Add order to the order book and return executed trades"""
        executed_trades = []
        # Ensure numeric defaults for orders instantiated outside the DB (tests)
        if getattr(order, "filled_quantity", None) is None:
            order.filled_quantity = 0
        if getattr(order, "status", None) is None:
            order.status = OrderStatus.OPEN
        
        if order.type == OrderType.BUY:
            # Try to match with existing sell orders
            while order.quantity > order.filled_quantity and self.sell_orders:
                best_sell = heapq.heappop(self.sell_orders)[1]
                # Defensive defaults for orders coming from tests (no DB defaults)
                if getattr(best_sell, "filled_quantity", None) is None:
                    best_sell.filled_quantity = 0
                if getattr(best_sell, "status", None) is None:
                    best_sell.status = OrderStatus.OPEN
                
                if best_sell.price > order.price:
                    # No more matches possible
                    heapq.heappush(self.sell_orders, (best_sell.price, best_sell))
                    break
                
                # Calculate possible trade quantity
                trade_quantity = min(
                    order.quantity - order.filled_quantity,
                    best_sell.quantity - best_sell.filled_quantity
                )
                
                # Execute trade
                trade_price = best_sell.price  # Price is the sell order's price
                executed_trades.append((
                    order.id, 
                    best_sell.id, 
                    trade_price, 
                    trade_quantity
                ))
                
                # Update order status
                order.filled_quantity += trade_quantity
                best_sell.filled_quantity += trade_quantity
                
                if best_sell.filled_quantity < best_sell.quantity:
                    # Mark as partially filled if some quantity matched, otherwise keep OPEN
                    best_sell.status = OrderStatus.PARTIALLY_FILLED if best_sell.filled_quantity > 0 else OrderStatus.OPEN
                    # Return to heap if not fully filled
                    heapq.heappush(self.sell_orders, (best_sell.price, best_sell))
                else:
                    best_sell.status = OrderStatus.FILLED
                
            # Add to order book if not fully filled
            if order.filled_quantity < order.quantity:
                heapq.heappush(self.buy_orders, (-order.price, order))
                order.status = OrderStatus.OPEN if order.filled_quantity == 0 else OrderStatus.PARTIALLY_FILLED
            else:
                order.status = OrderStatus.FILLED
                
        else:  # SELL order
            # Try to match with existing buy orders
            while order.quantity > order.filled_quantity and self.buy_orders:
                best_buy = heapq.heappop(self.buy_orders)[1]
                # Defensive defaults
                if getattr(best_buy, "filled_quantity", None) is None:
                    best_buy.filled_quantity = 0
                if getattr(best_buy, "status", None) is None:
                    best_buy.status = OrderStatus.OPEN
                
                if best_buy.price < order.price:
                    # No more matches possible
                    heapq.heappush(self.buy_orders, (-best_buy.price, best_buy))
                    break
                
                # Calculate possible trade quantity
                trade_quantity = min(
                    order.quantity - order.filled_quantity,
                    best_buy.quantity - best_buy.filled_quantity
                )
                
                # Execute trade
                trade_price = best_buy.price  # Price is the buy order's price
                executed_trades.append((
                    best_buy.id, 
                    order.id, 
                    trade_price, 
                    trade_quantity
                ))
                
                # Update order status
                order.filled_quantity += trade_quantity
                best_buy.filled_quantity += trade_quantity
                
                if best_buy.filled_quantity < best_buy.quantity:
                        # Mark as partially filled if some quantity matched, otherwise keep OPEN
                        best_buy.status = OrderStatus.PARTIALLY_FILLED if best_buy.filled_quantity > 0 else OrderStatus.OPEN
                        # Return to heap if not fully filled
                        heapq.heappush(self.buy_orders, (-best_buy.price, best_buy))
                else:
                    best_buy.status = OrderStatus.FILLED
                
            # Add to order book if not fully filled
            if order.filled_quantity < order.quantity:
                heapq.heappush(self.sell_orders, (order.price, order))
                order.status = OrderStatus.OPEN if order.filled_quantity == 0 else OrderStatus.PARTIALLY_FILLED
            else:
                order.status = OrderStatus.FILLED
                
        self.orders[order.id] = order
        return executed_trades
    
    def cancel_order(self, order_id: int) -> bool:
        """Cancel an order from the order book"""
        if order_id not in self.orders:
            return False
            
        order = self.orders[order_id]
        order.status = OrderStatus.CANCELLED
        
        # Remove from appropriate heap
        if order.type == OrderType.BUY:
            self.buy_orders = [(p, o) for p, o in self.buy_orders if o.id != order_id]
            heapq.heapify(self.buy_orders)
        else:
            self.sell_orders = [(p, o) for p, o in self.sell_orders if o.id != order_id]
            heapq.heapify(self.sell_orders)
            
        del self.orders[order_id]
        return True
    
    def get_order_book(self) -> Dict:
        """Return current state of the order book"""
        buy_orders = sorted([(-p, o) for p, o in self.buy_orders], key=lambda x: x[0], reverse=True)
        sell_orders = sorted(self.sell_orders, key=lambda x: x[0])
        
        return {
            "bids": [{"price": price, "quantity": order.quantity - order.filled_quantity} 
                    for price, order in buy_orders],
            "asks": [{"price": price, "quantity": order.quantity - order.filled_quantity} 
                    for price, order in sell_orders]
        }