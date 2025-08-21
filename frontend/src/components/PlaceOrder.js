import React, { useState } from 'react';

const PlaceOrder = () => {
  const [orderType, setOrderType] = useState('buy');
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const token = localStorage.getItem('token');
    const response = await fetch('/api/v1/orders/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        type: orderType,
        price: parseFloat(price),
        quantity: parseInt(quantity)
      })
    });

    if (response.ok) {
      alert('Order placed successfully');
      setPrice('');
      setQuantity('');
    } else {
      alert('Failed to place order');
    }
  };

  return (
    <div>
      <h2>Place New Order</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Order Type:</label>
          <select value={orderType} onChange={(e) => setOrderType(e.target.value)}>
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
        </div>
        <div className="form-group">
          <label>Price:</label>
          <input
            type="number"
            step="0.01"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Quantity:</label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            required
          />
        </div>
        <button type="submit">Place Order</button>
      </form>
    </div>
  );
};

export default PlaceOrder;