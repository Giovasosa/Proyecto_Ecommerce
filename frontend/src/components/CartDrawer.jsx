import React, { useState } from 'react';
import { X, Trash2, Tag } from 'lucide-react';
import { useCart } from '../context/CartContext';
import './CartDrawer.css';

const CartDrawer = () => {
  const { isCartOpen, toggleCart, cartItems, removeFromCart, cartTotal } = useCart();
  const [couponCode, setCouponCode] = useState('');

  const handleCheckout = async () => {
    try {
      const items = cartItems.map(item => ({
        product_variant_id: item.variant.id,
        quantity: item.quantity
      }));

      const orderData = {
        first_name: "Cliente",
        last_name: "Prueba",
        email: "test_user_123@testuser.com",
        phone: "0981000000",
        address: "Asunción, Paraguay",
        items: items,
        coupon_code: couponCode || null
      };

      const response = await fetch('http://127.0.0.1:8000/api/checkout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
      });

      const data = await response.json();

      if (response.ok && data.init_point) {
        window.location.href = data.sandbox_init_point || data.init_point;
      } else {
        alert("Atención: " + (data.error || JSON.stringify(data)));
        console.error("Error backend:", data);
      }
    } catch (error) {
      console.error("Error en el checkout:", error);
      alert("Hubo un problema de conexión con el servidor. ¿Está encendido el backend?");
    }
  };

  return (
    <>
      <div className={`cart-overlay ${isCartOpen ? 'open' : ''}`} onClick={toggleCart}></div>
      <div className={`cart-drawer glass-panel ${isCartOpen ? 'open' : ''}`}>
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
            Proceder al Pago
          </button>
        </div>
      </div>
    </>
  );
};

export default CartDrawer;
