import React, { useState } from 'react';
import { X, Trash2, Tag } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import './CartDrawer.css';

const CartDrawer = () => {
  const { isCartOpen, toggleCart, cartItems, removeFromCart, clearCart, cartTotal } = useCart();
  const [couponCode, setCouponCode] = useState('');

  const navigate = useNavigate();

  const handleCheckout = () => {
    toggleCart();
    navigate('/checkout');
  };

  return (
    <>
      <div className={`cart-overlay ${isCartOpen ? 'open' : ''}`} onClick={toggleCart}></div>
      <div className={`cart-drawer ${isCartOpen ? 'open' : ''}`}>
        <div className="cart-header">
          <h2>Tu Carrito</h2>
          <button className="btn-icon" onClick={toggleCart}>
            <X size={20} />
          </button>
        </div>

        <div className="cart-items">
          {cartItems.length === 0 ? (
            <div className="empty-cart">
              <p>Tu carrito está vacío</p>
            </div>
          ) : (
            cartItems.map((item, index) => (
              <div key={`${item.variant.id}-${index}`} className="cart-item glass-panel">
                <div className="item-details">
                  <h4>{item.product.name}</h4>
                  <p className="item-variant">{item.variant.model_name} | {item.variant.color}</p>
                  <p className="item-price">Gs. {item.variant.price} x {item.quantity}</p>
                </div>
                <button 
                  className="remove-btn" 
                  onClick={() => removeFromCart(item.variant.id)}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))
          )}
        </div>

        <div className="cart-footer">
          {cartItems.length > 0 && (
            <div className="coupon-section">
              <div className="coupon-input-group">
                <Tag size={16} className="coupon-icon" />
                <input 
                  type="text" 
                  placeholder="Código de cupón" 
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value)}
                  className="coupon-input"
                />
              </div>
            </div>
          )}
          <div className="cart-total">
            <span>Total:</span>
            <span>Gs. {cartTotal}</span>
          </div>
          <button 
            className="btn-primary checkout-btn" 
            disabled={cartItems.length === 0}
            onClick={handleCheckout}
          >
            Confirmar Pedido
          </button>
        </div>
      </div>
    </>
  );
};

export default CartDrawer;
