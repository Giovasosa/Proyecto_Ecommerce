import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { toast } from 'sonner';
import PageTransition from '../components/PageTransition';
import './Checkout.css';

const Checkout = () => {
  const { cartItems, cartTotal, clearCart } = useCart();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Si el carrito está vacío, redirigir al inicio
    if (cartItems.length === 0) {
      navigate('/');
      toast.info('Tu carrito está vacío');
    }
  }, [cartItems, navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validación básica
    if (!formData.first_name || !formData.last_name || !formData.phone || !formData.address) {
      toast.error('Por favor completa todos los campos requeridos');
      return;
    }

    setIsSubmitting(true);

    try {
      const items = cartItems.map(item => ({
        product_variant_id: item.variant.id,
        quantity: item.quantity
      }));

      const orderData = {
        ...formData,
        items: items
      };

      const headers = {
        'Content-Type': 'application/json',
      };
      const token = localStorage.getItem('access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('http://127.0.0.1:8000/api/checkout/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(orderData)
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("¡Pedido recibido con éxito! Nos pondremos en contacto contigo pronto.");
        // clearCart() will be called in ThankYou page to prevent conflicting redirects
        navigate('/gracias', { state: { orderId: data.order_id } });
      } else {
        toast.error("Error: " + (data.error || "Hubo un problema procesando tu orden"));
        console.error("Error backend:", data);
      }
    } catch (error) {
      console.error("Error en el checkout:", error);
      toast.error("Hubo un problema de conexión con el servidor.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (cartItems.length === 0) return null;

  return (
    <PageTransition>
      <div className="checkout-page container">
        <div className="page-header text-center">
          <h1>Finalizar Compra</h1>
          <p className="subtitle">Completa tus datos para el envío (Pago contra entrega)</p>
        </div>

        <div className="checkout-grid">
          <div className="checkout-form-container glass-panel">
            <h2>Datos de Envío</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="first_name">Nombre *</label>
                  <input 
                    type="text" 
                    id="first_name" 
                    name="first_name" 
                    value={formData.first_name} 
                    onChange={handleInputChange} 
                    required 
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="last_name">Apellido *</label>
                  <input 
                    type="text" 
                    id="last_name" 
                    name="last_name" 
                    value={formData.last_name} 
                    onChange={handleInputChange} 
                    required 
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input 
                  type="email" 
                  id="email" 
                  name="email" 
                  value={formData.email} 
                  onChange={handleInputChange} 
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">Teléfono (WhatsApp) *</label>
                <input 
                  type="tel" 
                  id="phone" 
                  name="phone" 
                  value={formData.phone} 
                  onChange={handleInputChange} 
                  required 
                />
              </div>

              <div className="form-group">
                <label htmlFor="address">Dirección de entrega completa *</label>
                <input 
                  type="text" 
                  id="address" 
                  name="address" 
                  value={formData.address} 
                  onChange={handleInputChange} 
                  placeholder="Ej: Calle Principal 123, Barrio Centro, Asunción"
                  required 
                />
              </div>
            </form>
          </div>

          <div className="checkout-summary glass-panel">
            <h3>Resumen del Pedido</h3>
            <div className="summary-items">
              {cartItems.map((item, index) => (
                <div key={index} className="summary-item">
                  <div className="summary-item-info">
                    <h4>{item.product.name}</h4>
                    <span className="summary-item-meta">{item.variant.model_name} | {item.variant.color} x {item.quantity}</span>
                  </div>
                  <div className="summary-item-price">
                    Gs. {item.variant.price * item.quantity}
                  </div>
                </div>
              ))}
            </div>

            <div className="summary-total">
              <span>Total a pagar</span>
              <span>Gs. {cartTotal}</span>
            </div>

            <p className="text-sm text-center" style={{marginBottom: '15px', color: 'var(--text-secondary)'}}>
              Pagarás al recibir tu pedido en efectivo o transferencia.
            </p>

            <button 
              className="btn-primary confirm-order-btn" 
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Procesando...' : 'Confirmar Pedido'}
            </button>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Checkout;
