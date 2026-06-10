import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import PageTransition from '../components/PageTransition';
import './Auth.css';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    let success = false;
    if (isLogin) {
      success = await login(formData.username, formData.password);
    } else {
      success = await register(formData.username, formData.email, formData.password);
    }

    setIsLoading(false);
    
    if (success) {
      navigate('/');
    }
  };

  return (
    <PageTransition>
      <div className="auth-page">
        <div className="auth-container glass-panel">
          <div className="auth-header">
            <h2>{isLogin ? 'Iniciar Sesión' : 'Crear Cuenta'}</h2>
            <p>
              {isLogin 
                ? 'Ingresa tus credenciales para acceder a tu cuenta.' 
                : 'Únete para gestionar tus pedidos y guardar tus direcciones.'}
            </p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">Usuario</label>
              <input 
                type="text" 
                id="username" 
                name="username" 
                value={formData.username} 
                onChange={handleInputChange} 
                required 
              />
            </div>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input 
                  type="email" 
                  id="email" 
                  name="email" 
                  value={formData.email} 
                  onChange={handleInputChange} 
                  required 
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="password">Contraseña</label>
              <input 
                type="password" 
                id="password" 
                name="password" 
                value={formData.password} 
                onChange={handleInputChange} 
                required 
              />
            </div>

            <button 
              type="submit" 
              className="btn-primary auth-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? 'Procesando...' : (isLogin ? 'Ingresar' : 'Registrarse')}
            </button>
          </form>

          <div className="auth-toggle">
            {isLogin ? '¿No tienes una cuenta?' : '¿Ya tienes una cuenta?'}
            <button onClick={() => setIsLogin(!isLogin)} type="button">
              {isLogin ? 'Regístrate aquí' : 'Inicia sesión'}
            </button>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Auth;
