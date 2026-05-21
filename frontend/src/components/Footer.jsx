import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.jpg';
import { Instagram, Facebook, Twitter } from 'lucide-react';
import './Footer.css';

const Footer = () => (
  <footer className="footer">
    <div className="container footer-inner">
      <div className="footer-brand">
        <img src={logo} alt="KR Cases" className="footer-logo" />
        <p>Fundas premium para smartphones de alta gama. Calidad y diseño sin compromiso.</p>
        <div className="social-links">
          <a href="#" aria-label="Instagram"><Instagram size={18} /></a>
          <a href="#" aria-label="Facebook"><Facebook size={18} /></a>
          <a href="#" aria-label="Twitter"><Twitter size={18} /></a>
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
          <li><a href="#">Preguntas frecuentes</a></li>
          <li><a href="#">Política de devoluciones</a></li>
          <li><a href="#">Contacto</a></li>
        </ul>
      </div>

      <div className="footer-col">
        <h4>Contacto</h4>
        <ul>
          <li><span>Asunción, Paraguay</span></li>
          <li><a href="mailto:info@krcases.com">info@krcases.com</a></li>
          <li><a href="https://wa.me/595981000000">WhatsApp</a></li>
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
