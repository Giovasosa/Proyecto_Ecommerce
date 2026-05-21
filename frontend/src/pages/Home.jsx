import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Shield, Truck, Star } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import './Home.css';
import case1Img from '../assets/case1.png';
import case2Img from '../assets/case2.png';
import heroImg from '../assets/hero.png';

const mockProducts = [
  {
    id: 1,
    name: "Obsidian Dark Silicone",
    base_price: "120000",
    category: { name: "Silicone Premium" },
    variants: [{ id: 101, model_name: "iPhone 15 Pro", color: "Dark Black", price: 120000, stock: 10 }]
  },
  {
    id: 2,
    name: "Crystal Titanium Clear",
    base_price: "150000",
    category: { name: "Transparent Series" },
    variants: [{ id: 102, model_name: "iPhone 15 Pro Max", color: "Clear", price: 150000, stock: 5 }]
  },
  {
    id: 3,
    name: "Matte Black Edition",
    base_price: "135000",
    category: { name: "Matte Series" },
    variants: [{ id: 103, model_name: "Samsung S24 Ultra", color: "Matte Black", price: 135000, stock: 8 }]
  },
  {
    id: 4,
    name: "Urban Leather Case",
    base_price: "180000",
    category: { name: "Leather Premium" },
    variants: [{ id: 104, model_name: "iPhone 15", color: "Black", price: 180000, stock: 3 }]
  },
];

const Home = () => {
  const [products, setProducts] = useState(mockProducts);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/products/')
      .then(res => res.json())
      .then(data => { if (data && data.length > 0) setProducts(data); })
      .catch(() => {});
  }, []);

  const images = [case1Img, case2Img, case1Img, case2Img];

  return (
    <div className="home-page">

      {/* ── HERO ── */}
      <section className="hero">
        <div className="container hero-content">
          <div className="hero-text">
            <span className="hero-eyebrow">Nueva Colección 2025</span>
            <h1>Eleva el nivel<br />de tu smartphone.</h1>
            <p>Diseño premium, protección absoluta. Fundas exclusivas para dispositivos de alta gama, hechas para quienes exigen lo mejor.</p>
            <div className="hero-buttons">
              <Link to="/catalogo" className="btn-primary">
                Ver Colección <ArrowRight size={16} style={{marginLeft: 6, display: 'inline'}} />
              </Link>
              <Link to="/catalogo" className="btn-secondary">Explorar Modelos</Link>
            </div>
          </div>
          <div className="hero-image-wrapper">
            <div className="hero-image-frame">
              <img src={heroImg} alt="KR Cases Premium" className="hero-image floating" />
            </div>
          </div>
        </div>
      </section>

      {/* ── BRAND STRIP ── */}
      <section className="brand-strip">
        <div className="container brand-strip-inner">
          <div className="brand-stat">
            <span className="brand-stat-number">+2000</span>
            <span className="brand-stat-label">Clientes satisfechos</span>
          </div>
          <div className="brand-divider" />
          <div className="brand-stat">
            <span className="brand-stat-number">50+</span>
            <span className="brand-stat-label">Modelos disponibles</span>
          </div>
          <div className="brand-divider" />
          <div className="brand-stat">
            <span className="brand-stat-number">100%</span>
            <span className="brand-stat-label">Calidad garantizada</span>
          </div>
          <div className="brand-divider" />
          <div className="brand-stat">
            <span className="brand-stat-number">24hs</span>
            <span className="brand-stat-label">Envío express</span>
          </div>
        </div>
      </section>

      {/* ── FEATURED PRODUCTS ── */}
      <section className="featured-products">
        <div className="container">
          <div className="section-header">
            <div>
              <span className="section-eyebrow">Colección</span>
              <h2>Productos Destacados</h2>
            </div>
            <Link to="/catalogo" className="view-all">
              Ver todo <ArrowRight size={14} style={{marginLeft: 4, display: 'inline'}} />
            </Link>
          </div>
          <div className="products-grid">
            {products.map((product, index) => (
              <ProductCard key={product.id} product={product} image={images[index % images.length]} />
            ))}
          </div>
        </div>
      </section>

      {/* ── WHY US ── */}
      <section className="why-us">
        <div className="container">
          <div className="section-header centered">
            <span className="section-eyebrow">¿Por qué elegirnos?</span>
            <h2>La diferencia KR Cases</h2>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon"><Shield size={28} /></div>
              <h3>Protección Extrema</h3>
              <p>Materiales de alta ingeniería que absorben impactos sin comprometer el diseño de tu dispositivo.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Star size={28} /></div>
              <h3>Diseño Premium</h3>
              <p>Cada funda es diseñada con atención al detalle. Elegante, minimalista y sofisticada.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Truck size={28} /></div>
              <h3>Envío Rápido</h3>
              <p>Despacho en 24hs a todo el país. Empaque premium que hace que cada compra sea especial.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA BANNER ── */}
      <section className="cta-banner">
        <div className="container cta-content">
          <h2>¿Listo para proteger tu dispositivo?</h2>
          <p>Encontrá la funda perfecta para tu modelo. Enviamos a todo el Paraguay.</p>
          <Link to="/catalogo" className="btn-primary">
            Explorar catálogo <ArrowRight size={16} style={{marginLeft: 6, display: 'inline'}} />
          </Link>
        </div>
      </section>

    </div>
  );
};

export default Home;
