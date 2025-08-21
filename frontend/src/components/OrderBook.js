import React from 'react';
import useWebSocket from '../hooks/useWebSocket';

const OrderBook = () => {
  const orderBookData = useWebSocket('ws://localhost:8000/api/v1/ws/orderbook');
  
  if (!orderBookData) {
    return <div>Loading order book...</div>;
  }

  return (
    <div className="order-book">
      <h2>Order Book</h2>
      <div className="order-book-container">
        <div className="bids">
          <h3>Bids (Buy Orders)</h3>
          <table>
            <thead>
              <tr>
                <th>Price</th>
                <th>Quantity</th>
              </tr>
            </thead>
            <tbody>
              {orderBookData.bids.map((bid, index) => (
                <tr key={index} className="bid-row">
                  <td>{bid.price.toFixed(2)}</td>
                  <td>{bid.quantity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="asks">
          <h3>Asks (Sell Orders)</h3>
          <table>
            <thead>
              <tr>
                <th>Price</th>
                <th>Quantity</th>
              </tr>
            </thead>
            <tbody>
              {orderBookData.asks.map((ask, index) => (
                <tr key={index} className="ask-row">
                  <td>{ask.price.toFixed(2)}</td>
                  <td>{ask.quantity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default OrderBook;