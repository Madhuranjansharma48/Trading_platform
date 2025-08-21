import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "./App.css";
import Dashboard from "./components/Dashboard";
import Login from "./components/Login";
import Navbar from "./components/Navbar";
import OrderBook from "./components/OrderBook";
import PlaceOrder from "./components/PlaceOrder";
import Signup from "./components/Signup";
import TradeHistory from "./components/TradeHistory";
import { AuthProvider } from "./context/AuthContext";

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <div className="container">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/" element={<Dashboard />} />
              <Route path="/orderbook" element={<OrderBook />} />
              <Route path="/history" element={<TradeHistory />} />
              <Route path="/order" element={<PlaceOrder />} />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
