import React, { useState, useEffect } from 'react';
import ProductCard from '../components/ProductCard';
import './Home.css';
import case1Img from '../assets/case1.png';
import case2Img from '../assets/case2.png';

const mockProducts = [
  {
    id: 1,
    name: "Obsidian Dark Silicone",
    base_price: "120000",
    category: { name: "Silicone Premium" },
    variants: [
      { id: 101, model_name: "iPhone 15 Pro", color: "Dark Purple", price: 120000 }
    ]
  },
  {
    id: 2,
    name: "Crystal Titanium Clear",
    base_price: "150000",
    category: { name: "Transparent Series" },
    variants: [
      { id: 102, model_name: "iPhone 15 Pro Max", color: "Clear/Titanium", price: 150000 }
    ]
  }
];

const Home = () => {
  const [products, setProducts] = useState(mockProducts);

  useEffect(() => {
    // Intento de obtener productos reales
    fetch('http://127.0.0.1:8000/api/products/')
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          setProducts(data);
        }
      })
      .catch(err => console.log("Usando productos mock (Backend no responde o vacío)"));
  }, []);

  return (
    <div className="home-page">
      <section className="hero">
        <div className="container hero-content">
          <div className="hero-text">
            <h1>Eleva el nivel<br/>de tu smartphone.</h1>
            <p>Diseño premium, protección absoluta. Descubre nuestra nueva colección de fundas exclusivas para dispositivos de alta gama.</p>
            <div className="hero-buttons">
              <button className="btn-primary">Ver Colección</button>
              <button className="btn-secondary">Explorar Modelos</button>
            </div>
          </div>
          <div className="hero-image-wrapper">
             <div className="glow-effect"></div>
             <img src={case2Img} alt="Premium Case" className="hero-image floating" />
          </div>
        </div>
      </section>

      <section className="featured-products container">
        <div className="section-header">
          <h2>Destacados</h2>
          <a href="#" className="view-all">Ver todo el catálogo</a>
        </div>
        
        <div className="products-grid">
          {products.map((product, index) => (
            <ProductCard 
              key={product.id} 
              product={product} 
              image={index % 2 === 0 ? case1Img : case2Img} 
            />
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
