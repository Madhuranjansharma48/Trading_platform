import React, { useState, useEffect } from 'react';

const TradeHistory = () => {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    const fetchTrades = async () => {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/trades/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTrades(data);
      }
    };

    fetchTrades();
  }, []);

  return (
    <div>
      <h2>Trade History</h2>
      <table>
        <thead>
          <tr>
            <th>Price</th>
            <th>Quantity</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.id}>
              <td>{trade.price}</td>
              <td>{trade.quantity}</td>
              <td>{new Date(trade.executed_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TradeHistory;