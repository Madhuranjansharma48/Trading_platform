import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  return (
    <div>
      <h1>Dashboard</h1>
      <div className="dashboard-links">
        <Link to="/orderbook" className="dashboard-link">
          View Order Book
        </Link>
        <Link to="/order" className="dashboard-link">
          Place New Order
        </Link>
        <Link to="/history" className="dashboard-link">
          View Trade History
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;