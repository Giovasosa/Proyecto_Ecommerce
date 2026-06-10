import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.png';
import { AtSign, MessageCircle, Share2 } from 'lucide-react';
import './Footer.css';

const Footer = () => (
  <footer className="footer">
    <div className="container footer-inner">
      <div className="footer-brand">
        <img src={logo} alt="KR Cases" className="footer-logo" />
        <p>Fundas premium para smartphones de alta gama. Calidad y diseño sin compromiso.</p>
        <div className="social-links">
          <a href="#" aria-label="Instagram"><AtSign size={18} /></a>
          <a href="#" aria-label="Facebook"><Share2 size={18} /></a>
          <a href="#" aria-label="WhatsApp"><MessageCircle size={18} /></a>
        </div>
      </div>

      <div className="footer-col">
        <h4>Tienda</h4>
        <ul>
          <li><Link to="/catalogo">Catálogo</Link></li>
          <li><Link to="/">Novedades</Link></li>
          <li><Link to="/">Ofertas</Link></li>
        </ul>
      </div>

      <div className="footer-col">
        <h4>Soporte</h4>
        <ul>
          <li><Link to="/faq">Preguntas frecuentes</Link></li>
          <li><Link to="/devoluciones">Política de devoluciones</Link></li>
          <li><Link to="/contacto">Contacto</Link></li>
        </ul>
      </div>

      <div className="footer-col">
        <h4>Contacto</h4>
        <ul>
          <li><span>Asunción, Paraguay</span></li>
          <li><a href="mailto:info@krcases.com">info@krcases.com</a></li>
          <li><a href="https://wa.me/595991597314">WhatsApp</a></li>
        </ul>
      </div>
    </div>

    <div className="footer-bottom">
      <div className="container footer-bottom-inner">
        <span>© {new Date().getFullYear()} KR Cases. Todos los derechos reservados.</span>
        <span>Hecho en Paraguay 🇵🇾</span>
      </div>
    </div>
  </footer>
);

export default Footer;
