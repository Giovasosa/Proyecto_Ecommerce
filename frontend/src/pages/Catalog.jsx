import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ArrowRight, Filter, Grid, List, Search } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import PageTransition from '../components/PageTransition';
import './Catalog.css';
import case1Img from '../assets/case1.png';
import case2Img from '../assets/case2.png';
import case3Img from '../assets/case3.png';
import case4Img from '../assets/case4.png';

const CATEGORIES = ['Todos', 'Silicone Premium', 'Transparent Series', 'Matte Series', 'Leather Premium', 'Armor Series'];

const Catalog = () => {
  const location = useLocation();
  const [products, setProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('Todos');
  const [search, setSearch] = useState(location.state?.searchQuery || '');
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('default');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/products/')
      .then(res => res.json())
      .then(data => { 
        if (data && data.length > 0) {
          setProducts(data);
          setFiltered(data);
        }
        setLoading(false);
      })
      .catch(() => { setLoading(false); });
  }, []);

  useEffect(() => {
    let result = [...products];
    if (activeCategory !== 'Todos') {
      result = result.filter(p => p.category?.name === activeCategory);
    }
    if (search.trim()) {
      result = result.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));
    }
    if (sortBy === 'price-asc') result.sort((a, b) => +a.base_price - +b.base_price);
    if (sortBy === 'price-desc') result.sort((a, b) => +b.base_price - +a.base_price);
    setFiltered(result);
  }, [products, activeCategory, search, sortBy]);

  const localImages = [case1Img, case2Img, case3Img, case4Img, case1Img, case2Img];

  return (
    <PageTransition>
    <div className="catalog-page">
      {/* Header */}
      <div className="catalog-header">
        <div className="container">
          <div className="breadcrumb">
            <Link to="/">Inicio</Link>
            <span>/</span>
            <span>Catálogo</span>
          </div>
          <h1>Catálogo</h1>
          <p>Encontrá la funda perfecta para tu dispositivo</p>
        </div>
      </div>

      <div className="container catalog-body">
        {/* Sidebar */}
        <aside className="catalog-sidebar">
          <div className="filter-group">
            <h3 className="filter-title">Categorías</h3>
            <ul className="filter-list">
              {CATEGORIES.map(cat => (
                <li key={cat}>
                  <button
                    className={`filter-btn ${activeCategory === cat ? 'active' : ''}`}
                    onClick={() => setActiveCategory(cat)}
                  >
                    {cat}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="filter-group">
            <h3 className="filter-title">Precio</h3>
            <ul className="filter-list">
              {[
                { label: 'Menor precio', value: 'price-asc' },
                { label: 'Mayor precio', value: 'price-desc' },
                { label: 'Predeterminado', value: 'default' },
              ].map(opt => (
                <li key={opt.value}>
                  <button
                    className={`filter-btn ${sortBy === opt.value ? 'active' : ''}`}
                    onClick={() => setSortBy(opt.value)}
                  >
                    {opt.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* Main content */}
        <div className="catalog-main">
          {/* Toolbar */}
          <div className="catalog-toolbar">
            <div className="search-bar">
              <Search size={16} />
              <input
                type="text"
                placeholder="Buscar productos..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <div className="toolbar-right">
              <span className="results-count">{filtered.length} productos</span>
              <div className="view-toggle">
                <button className={viewMode === 'grid' ? 'active' : ''} onClick={() => setViewMode('grid')}>
                  <Grid size={16} />
                </button>
                <button className={viewMode === 'list' ? 'active' : ''} onClick={() => setViewMode('list')}>
                  <List size={16} />
                </button>
              </div>
            </div>
          </div>

          {/* Products */}
          {loading ? (
            <div className="no-results">
              <p>Cargando productos...</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="no-results">
              <p>No se encontraron productos con esos filtros.</p>
              <button className="btn-secondary" onClick={() => { setActiveCategory('Todos'); setSearch(''); }}>
                Limpiar filtros
              </button>
            </div>
          ) : (
            <div className={`catalog-grid ${viewMode === 'list' ? 'list-view' : ''}`}>
              {filtered.map((product, index) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  image={product.image || localImages[index % localImages.length]}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
    </PageTransition>
  );
};

export default Catalog;
