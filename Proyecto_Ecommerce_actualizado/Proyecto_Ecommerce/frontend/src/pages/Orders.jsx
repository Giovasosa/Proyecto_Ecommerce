import React, { useState, useEffect } from 'react';
import { Package, Download, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Orders.css';

const API_BASE = 'http://127.0.0.1:8000/api';

const STATUS_LABELS = {
  PENDING: { label: 'Pendiente', className: 'status-pending' },
  PAID: { label: 'Pagado', className: 'status-paid' },
  SHIPPED: { label: 'Enviado', className: 'status-shipped' },
  CANCELLED: { label: 'Cancelado', className: 'status-cancelled' },
};

const Orders = () => {
  const { authFetch } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    const loadOrders = async () => {
      try {
        const res = await authFetch(`${API_BASE}/orders/`);
        if (!res.ok) throw new Error('No se pudo cargar tu historial de pedidos');
        const data = await res.json();
        setOrders(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadOrders();
  }, [authFetch]);

  const handleDownloadInvoice = async (orderId) => {
    setDownloadingId(orderId);
    try {
      const res = await authFetch(`${API_BASE}/orders/${orderId}/invoice/`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || 'No se pudo descargar la factura');
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `factura_orden_${orderId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message);
    } finally {
      setDownloadingId(null);
    }
  };

  if (loading) return <div className="container orders-page"><p>Cargando tus pedidos...</p></div>;

  return (
    <div className="container orders-page">
      <div className="orders-header">
        <Package size={26} />
        <h1>Mis Pedidos</h1>
      </div>

      {error && <p className="orders-error">{error}</p>}

      {!error && orders.length === 0 && (
        <div className="empty-orders glass-panel">
          <p>Todavía no realizaste ningún pedido.</p>
        </div>
      )}

      <div className="orders-list">
        {orders.map((order) => {
          const statusInfo = STATUS_LABELS[order.status] || { label: order.status, className: '' };
          return (
            <div key={order.id} className="order-card glass-panel">
              <div className="order-card-header">
                <div>
                  <h3>Pedido #{order.id}</h3>
                  <span className="order-date">
                    {new Date(order.created_at).toLocaleDateString('es-PY', { year: 'numeric', month: 'long', day: 'numeric' })}
                  </span>
                </div>
                <span className={`order-status ${statusInfo.className}`}>{statusInfo.label}</span>
              </div>

              <div className="order-items">
                {order.items.map((item) => (
                  <div key={item.id} className="order-item-row">
                    <span>{item.quantity} x {item.product_name} <em>({item.variant_label})</em></span>
                    <span>Gs. {Number(item.price_at_purchase * item.quantity).toLocaleString('es-PY')}</span>
                  </div>
                ))}
              </div>

              <div className="order-card-footer">
                <span className="order-total">Total: Gs. {Number(order.total_amount).toLocaleString('es-PY')}</span>
                {order.invoice_available && (
                  <button
                    className="btn-secondary invoice-btn"
                    onClick={() => handleDownloadInvoice(order.id)}
                    disabled={downloadingId === order.id}
                  >
                    {downloadingId === order.id ? <Loader2 size={16} className="spin" /> : <Download size={16} />}
                    Descargar factura
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Orders;
