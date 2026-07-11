import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Lock, ShoppingBag, LogOut, Package } from 'lucide-react';
import PageTransition from '../components/PageTransition';
import './UserProfile.css';

const UserProfile = () => {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('data');
  const [isLoading, setIsLoading] = useState(false);
  
  // Data State
  const [userData, setUserData] = useState({
    first_name: '',
    last_name: '',
    email: ''
  });
  
  // Password State
  const [passData, setPassData] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: ''
  });

  // Orders State
  const [orders, setOrders] = useState([]);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    setUserData({
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email || ''
    });
    
    if (activeTab === 'orders') {
      fetchOrders();
    }
  }, [user, navigate, activeTab]);

  const fetchOrders = async () => {
    setOrdersLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/orders/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setOrders(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setOrdersLoading(false);
    }
  };

  const showMessage = (text, type = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 3000);
  };

  const handleDataUpdate = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/auth/me/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userData)
      });
      if (res.ok) {
        showMessage('Datos actualizados correctamente');
      } else {
        showMessage('Error al actualizar datos', 'error');
      }
    } catch (err) {
      showMessage('Error de conexión', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    if (passData.new_password !== passData.new_password_confirm) {
      showMessage('Las contraseñas nuevas no coinciden', 'error');
      return;
    }
    setIsLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/auth/password/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(passData)
      });
      if (res.ok) {
        showMessage('Contraseña cambiada con éxito');
        setPassData({ old_password: '', new_password: '', new_password_confirm: '' });
      } else {
        const err = await res.json();
        showMessage(err.old_password ? err.old_password[0] : 'Error al cambiar contraseña', 'error');
      }
    } catch (err) {
      showMessage('Error de conexión', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    if (window.confirm('¿Seguro que deseas salir?')) {
      logout();
      navigate('/');
    }
  };

  const handleDownloadInvoice = async (orderId) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/orders/${orderId}/invoice/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Factura_Pedido_${orderId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        const data = await res.json();
        showMessage(data.error || 'Error al descargar la factura', 'error');
      }
    } catch (err) {
      showMessage('Error de conexión al descargar', 'error');
    }
  };

  if (!user) return null;

  return (
    <PageTransition>
      <div className="profile-page container">
        <div className="profile-header">
          <h1>Hola, {user.username}</h1>
          <p>Gestiona tu cuenta y revisa tus pedidos.</p>
        </div>

        <div className="profile-layout">
          <aside className="profile-sidebar glass-panel">
            <nav className="profile-nav">
              <button 
                className={`profile-nav-btn ${activeTab === 'data' ? 'active' : ''}`}
                onClick={() => setActiveTab('data')}
              >
                <User size={18} /> Mis Datos
              </button>
              <button 
                className={`profile-nav-btn ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => setActiveTab('security')}
              >
                <Lock size={18} /> Seguridad
              </button>
              <button 
                className={`profile-nav-btn ${activeTab === 'orders' ? 'active' : ''}`}
                onClick={() => setActiveTab('orders')}
              >
                <ShoppingBag size={18} /> Mis Pedidos
              </button>
              <div className="profile-nav-divider" />
              <button className="profile-nav-btn text-danger" onClick={handleLogout}>
                <LogOut size={18} /> Cerrar Sesión
              </button>
            </nav>
          </aside>

          <main className="profile-content glass-panel">
            {message && (
              <div className={`profile-alert ${message.type}`}>
                {message.text}
              </div>
            )}

            {activeTab === 'data' && (
              <div className="profile-section fade-in">
                <h2>Información Personal</h2>
                <form onSubmit={handleDataUpdate} className="profile-form">
                  <div className="form-group">
                    <label>Nombre</label>
                    <input 
                      type="text" 
                      value={userData.first_name} 
                      onChange={e => setUserData({...userData, first_name: e.target.value})} 
                    />
                  </div>
                  <div className="form-group">
                    <label>Apellido</label>
                    <input 
                      type="text" 
                      value={userData.last_name} 
                      onChange={e => setUserData({...userData, last_name: e.target.value})} 
                    />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input 
                      type="email" 
                      value={userData.email} 
                      onChange={e => setUserData({...userData, email: e.target.value})} 
                      required
                    />
                  </div>
                  <button type="submit" className="btn-primary" disabled={isLoading}>
                    {isLoading ? 'Guardando...' : 'Guardar Cambios'}
                  </button>
                </form>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="profile-section fade-in">
                <h2>Cambiar Contraseña</h2>
                <form onSubmit={handlePasswordUpdate} className="profile-form">
                  <div className="form-group">
                    <label>Contraseña Actual</label>
                    <input 
                      type="password" 
                      value={passData.old_password} 
                      onChange={e => setPassData({...passData, old_password: e.target.value})} 
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Nueva Contraseña</label>
                    <input 
                      type="password" 
                      value={passData.new_password} 
                      onChange={e => setPassData({...passData, new_password: e.target.value})} 
                      required
                      minLength={8}
                    />
                  </div>
                  <div className="form-group">
                    <label>Confirmar Nueva Contraseña</label>
                    <input 
                      type="password" 
                      value={passData.new_password_confirm} 
                      onChange={e => setPassData({...passData, new_password_confirm: e.target.value})} 
                      required
                      minLength={8}
                    />
                  </div>
                  <button type="submit" className="btn-primary" disabled={isLoading}>
                    {isLoading ? 'Actualizando...' : 'Actualizar Contraseña'}
                  </button>
                </form>
              </div>
            )}

            {activeTab === 'orders' && (
              <div className="profile-section fade-in">
                <h2>Historial de Pedidos</h2>
                {ordersLoading ? (
                  <p>Cargando pedidos...</p>
                ) : orders.length === 0 ? (
                  <div className="empty-state">
                    <Package size={48} />
                    <p>Aún no has realizado ninguna compra.</p>
                  </div>
                ) : (
                  <div className="orders-list">
                    {orders.map(order => (
                      <div key={order.id} className="order-card">
                        <div className="order-header">
                          <div>
                            <span className="order-id">Pedido #{order.id}</span>
                            <span className="order-date">
                              {new Date(order.created_at).toLocaleDateString('es-PY')}
                            </span>
                          </div>
                          <span className={`order-status ${order.status.toLowerCase()}`}>
                            {order.status === 'PAID' ? 'Pagado' : 'Pendiente'}
                          </span>
                        </div>
                        <div className="order-body">
                          {order.items.map(item => (
                            <div key={item.id} className="order-item">
                              <span>{item.quantity}x {item.product_variant.product.name} ({item.product_variant.color})</span>
                              <span>Gs. {(item.price_at_purchase * item.quantity).toLocaleString('es-PY')}</span>
                            </div>
                          ))}
                        </div>
                        <div className="order-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <button 
                            onClick={() => handleDownloadInvoice(order.id)} 
                            className="btn-primary" 
                            style={{ padding: '6px 12px', fontSize: '12px' }}
                          >
                            📄 Descargar Factura
                          </button>
                          <strong>Total: Gs. {order.total_amount.toLocaleString('es-PY')}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </main>
        </div>
      </div>
    </PageTransition>
  );
};

export default UserProfile;
