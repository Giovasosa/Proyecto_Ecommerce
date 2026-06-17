import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingBag, Search, User, X } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import CartDrawer from './CartDrawer';
import logo from '../assets/logo.png';
import './Navbar.css';

const Navbar = () => {
  const { cartCount, toggleCart } = useCart();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchSubmit = (e) => {
    if (e.key === 'Enter' && searchQuery.trim() !== '') {
      navigate('/catalogo', { state: { searchQuery } });
      setIsSearchOpen(false);
      setSearchQuery('');
    }
  };

  const handleUserClick = () => {
    if (user) {
      if (window.confirm('¿Deseas cerrar sesión?')) {
        logout();
      }
    } else {
      navigate('/auth');
    }
  };

  return (
    <>
      <nav className="navbar glass-panel">
        <div className="navbar-container container">
          <div className="nav-left">
            <Link to="/" className="logo">
              <img src={logo} alt="KR Cases" className="logo-img" />
            </Link>
          </div>

          <div className="nav-center desktop-only">
            <ul className="nav-links">
              <li><Link to="/">Inicio</Link></li>
              <li><Link to="/catalogo">Catálogo</Link></li>

            </ul>
          </div>

          <div className="nav-right">
            <div className={`nav-search ${isSearchOpen ? 'open' : ''}`}>
              {isSearchOpen && (
                <input 
                  type="text" 
                  placeholder="Buscar fundas..." 
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  onKeyDown={handleSearchSubmit}
                  autoFocus
                />
              )}
              <button 
                className="btn-icon" 
                aria-label="Search" 
                onClick={() => setIsSearchOpen(!isSearchOpen)}
              >
                {isSearchOpen ? <X size={20} /> : <Search size={20} />}
              </button>
            </div>
            <button className="btn-icon" aria-label="User" onClick={handleUserClick} title={user ? user.username : 'Iniciar sesión'}>
              <User size={20} />
            </button>
            <button className="btn-icon cart-btn" onClick={toggleCart} aria-label="Cart">
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
