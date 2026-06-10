import React, { useState } from 'react';
import { Mail, MessageCircle, MapPin } from 'lucide-react';
import { toast } from 'sonner';
import PageTransition from '../components/PageTransition';
import './SupportPages.css';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simular envío
    toast.success('¡Mensaje enviado con éxito! Nos pondremos en contacto contigo pronto.');
    setFormData({ name: '', email: '', subject: '', message: '' });
  };

  return (
    <PageTransition>
      <div className="support-page container">
        <div className="support-header">
          <h1>Contacto</h1>
          <p>¿Tienes alguna duda o consulta especial? Escríbenos y te responderemos lo antes posible.</p>
        </div>

        <div className="support-content">
          <div className="contact-grid">
            
            <div className="contact-info">
              <div className="contact-card">
                <div className="icon">
                  <MessageCircle size={24} />
                </div>
                <h3>WhatsApp</h3>
                <p>Atención inmediata</p>
                <a href="https://wa.me/595991597314" target="_blank" rel="noreferrer">+595 991 597 314</a>
              </div>

              <div className="contact-card">
                <div className="icon">
                  <Mail size={24} />
                </div>
                <h3>Email</h3>
                <p>Consultas y soporte</p>
                <a href="mailto:info@krcases.com">info@krcases.com</a>
              </div>

              <div className="contact-card">
                <div className="icon">
                  <MapPin size={24} />
                </div>
                <h3>Ubicación</h3>
                <p>Asunción, Paraguay</p>
                <p style={{fontSize: '0.85rem', marginTop: '5px'}}>Solo tienda online. Envíos a todo el país.</p>
              </div>
            </div>

            <div className="contact-form">
              <h2 style={{fontSize: '1.5rem', marginBottom: '20px'}}>Envíanos un mensaje</h2>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Nombre</label>
                  <input 
                    type="text" 
                    name="name" 
                    value={formData.name}
                    onChange={handleChange}
                    required 
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input 
                    type="email" 
                    name="email" 
                    value={formData.email}
                    onChange={handleChange}
                    required 
                  />
                </div>
                <div className="form-group">
                  <label>Asunto</label>
                  <input 
                    type="text" 
                    name="subject" 
                    value={formData.subject}
                    onChange={handleChange}
                    required 
                  />
                </div>
                <div className="form-group">
                  <label>Mensaje</label>
                  <textarea 
                    name="message" 
                    value={formData.message}
                    onChange={handleChange}
                    required 
                  />
                </div>
                <button type="submit" className="btn-primary" style={{width: '100%', marginTop: '10px'}}>
                  Enviar Mensaje
                </button>
              </form>
            </div>

          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Contact;
