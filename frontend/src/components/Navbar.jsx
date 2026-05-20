import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBag, Search, Menu } from 'lucide-react';
import { useCart } from '../context/CartContext';
import CartDrawer from './CartDrawer';
import './Navbar.css';

const Navbar = () => {
  const { cartCount, toggleCart } = useCart();

  return (
    <>
      <nav className="navbar glass-panel">
        <div className="navbar-container container">
          <div className="nav-left">
            <button className="btn-icon mobile-menu">
              <Menu size={20} />
            </button>
            <Link to="/" className="logo">
              KR <span>CASES</span>
            </Link>
          </div>

          <div className="nav-center desktop-only">
            <ul className="nav-links">
              <li><Link to="/">Inicio</Link></li>
              <li><Link to="/">Catálogo</Link></li>
              <li><Link to="/">Colecciones</Link></li>
            </ul>
          </div>

          <div className="nav-right">
            <button className="btn-icon desktop-only">
              <Search size={20} />
            </button>
            <button className="btn-icon cart-btn" onClick={toggleCart}>
              <ShoppingBag size={20} />
              {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
            </button>
          </div>
        </div>
      </nav>
      <CartDrawer />
    </>
  );
};

export default Navbar;
