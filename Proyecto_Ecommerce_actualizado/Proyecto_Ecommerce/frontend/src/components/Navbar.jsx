import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingBag, Search, Menu, User, Package, BarChart3, LogOut } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import CartDrawer from './CartDrawer';
import './Navbar.css';

const Navbar = () => {
  const { cartCount, toggleCart } = useCart();
  const { isAuthenticated, isAdmin, user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate('/');
  };

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

            <div className="user-menu" ref={menuRef}>
              <button className="btn-icon" onClick={() => setMenuOpen((o) => !o)} title="Cuenta">
                <User size={20} />
              </button>
              {menuOpen && (
                <div className="user-dropdown glass-panel">
                  {isAuthenticated ? (
                    <>
                      <span className="user-dropdown-name">Hola, {user?.username}</span>
                      <Link to="/orders" onClick={() => setMenuOpen(false)}>
                        <Package size={16} /> Mis pedidos
                      </Link>
                      {isAdmin && (
                        <Link to="/reports" onClick={() => setMenuOpen(false)}>
                          <BarChart3 size={16} /> Reportes de ventas
                        </Link>
                      )}
                      <button onClick={handleLogout} className="user-dropdown-logout">
                        <LogOut size={16} /> Cerrar sesión
                      </button>
                    </>
                  ) : (
                    <>
                      <Link to="/login" onClick={() => setMenuOpen(false)}>Iniciar sesión</Link>
                      <Link to="/register" onClick={() => setMenuOpen(false)}>Crear cuenta</Link>
                    </>
                  )}
                </div>
              )}
            </div>

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
