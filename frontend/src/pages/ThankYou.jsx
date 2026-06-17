import React, { useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import PageTransition from '../components/PageTransition';
import './ThankYou.css';

const ThankYou = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { clearCart } = useCart();
  const orderId = location.state?.orderId;

  useEffect(() => {
    // Si entran directamente a la ruta sin haber comprado, redirigir al inicio
    if (!orderId) {
      navigate('/');
    } else {
      // Limpiamos el carrito al llegar aquí exitosamente
      clearCart();
    }
  }, [orderId, navigate, clearCart]);

  if (!orderId) return null;

  return (
    <PageTransition>
      <div className="thankyou-page container">
        <div className="thankyou-card glass-panel text-center">
          <div className="success-icon-wrapper">
            <svg className="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
              <circle className="checkmark__circle" cx="26" cy="26" r="25" fill="none" />
              <path className="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
            </svg>
          </div>
          
          <h1 className="thankyou-title">¡Gracias por tu compra!</h1>
          <p className="thankyou-subtitle">Hemos recibido tu pedido correctamente.</p>
          
          <div className="order-reference">
            <span>Referencia del Pedido:</span>
            <strong>#{orderId}</strong>
          </div>
          
          <div className="thankyou-details">
            <p>
              Te hemos enviado un correo electrónico con los detalles completos de tu orden.
            </p>
            <p className="payment-reminder">
              <i className="fas fa-box-open"></i> Recuerda que pagarás al momento de recibir tu producto.
            </p>
          </div>
          
          <div className="thankyou-actions">
            <Link to="/catalogo" className="btn-primary">
              Seguir Comprando
            </Link>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default ThankYou;
