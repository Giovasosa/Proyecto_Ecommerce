import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const initialForm = {
  username: '', email: '', first_name: '', last_name: '', password: '', password2: '',
};

const Register = () => {
  const { register, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await register(form);
      setSuccess(true);
      // Login automático luego de registrarse
      await login(form.username, form.password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'No se pudo completar el registro');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page container">
      <div className="auth-card glass-panel">
        <div className="auth-icon"><UserPlus size={28} /></div>
        <h1>Crear cuenta</h1>
        <p className="auth-subtitle">Registrate para comprar más rápido y ver tu historial de pedidos.</p>

        {error && <div className="auth-error">{error}</div>}
        {success && !error && <div className="auth-success">¡Cuenta creada! Iniciando sesión...</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Usuario
            <input type="text" name="username" value={form.username} onChange={handleChange} required autoFocus />
          </label>
          <label>
            Email
            <input type="email" name="email" value={form.email} onChange={handleChange} required />
          </label>
          <div className="auth-form-row">
            <label>
              Nombre
              <input type="text" name="first_name" value={form.first_name} onChange={handleChange} />
            </label>
            <label>
              Apellido
              <input type="text" name="last_name" value={form.last_name} onChange={handleChange} />
            </label>
          </div>
          <label>
            Contraseña
            <input type="password" name="password" value={form.password} onChange={handleChange} required minLength={8} />
          </label>
          <label>
            Repetir contraseña
            <input type="password" name="password2" value={form.password2} onChange={handleChange} required minLength={8} />
          </label>
          <button type="submit" className="btn-primary auth-submit" disabled={submitting}>
            {submitting ? 'Creando cuenta...' : 'Registrarme'}
          </button>
        </form>

        <p className="auth-switch">
          ¿Ya tenés cuenta? <Link to="/login">Iniciar sesión</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
