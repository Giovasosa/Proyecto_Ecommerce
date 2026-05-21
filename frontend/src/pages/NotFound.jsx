import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import './NotFound.css';

const NotFound = () => (
  <div className="not-found-page container">
    <div className="not-found-inner">
      <span className="not-found-code">404</span>
      <h1>Página no encontrada</h1>
      <p>La página que buscás no existe o fue movida.</p>
      <Link to="/" className="btn-primary">
        <ArrowLeft size={16} style={{ marginRight: 8 }} />
        Volver al inicio
      </Link>
    </div>
  </div>
);

export default NotFound;
