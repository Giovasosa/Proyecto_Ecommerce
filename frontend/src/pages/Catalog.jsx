import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Filter, Grid, List, Search } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import PageTransition from '../components/PageTransition';
import './Catalog.css';
import case1Img from '../assets/case1.png';
import case2Img from '../assets/case2.png';

const mockProducts = [
  { id: 1, name: "Obsidian Dark Silicone", base_price: "120000", category: { name: "Silicone Premium" }, variants: [{ id: 101, model_name: "iPhone 15 Pro", color: "Dark Black", price: 120000, stock: 10 }] },
  { id: 2, name: "Crystal Titanium Clear", base_price: "150000", category: { name: "Transparent Series" }, variants: [{ id: 102, model_name: "iPhone 15 Pro Max", color: "Clear", price: 150000, stock: 5 }] },
  { id: 3, name: "Matte Black Edition", base_price: "135000", category: { name: "Matte Series" }, variants: [{ id: 103, model_name: "Samsung S24 Ultra", color: "Matte Black", price: 135000, stock: 8 }] },
  { id: 4, name: "Urban Leather Case", base_price: "180000", category: { name: "Leather Premium" }, variants: [{ id: 104, model_name: "iPhone 15", color: "Black", price: 180000, stock: 3 }] },
  { id: 5, name: "Shadow Flex Armor", base_price: "110000", category: { name: "Armor Series" }, variants: [{ id: 105, model_name: "Samsung A54", color: "Black", price: 110000, stock: 12 }] },
  { id: 6, name: "Minimal Frost Case", base_price: "95000", category: { name: "Transparent Series" }, variants: [{ id: 106, model_name: "iPhone 14", color: "Frost White", price: 95000, stock: 7 }] },
];

const CATEGORIES = ['Todos', 'Silicone Premium', 'Transparent Series', 'Matte Series', 'Leather Premium', 'Armor Series'];

const Catalog = () => {
  const [products, setProducts] = useState(mockProducts);
  const [filtered, setFiltered] = useState(mockProducts);
  const [activeCategory, setActiveCategory] = useState('Todos');
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('default');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/products/')
      .then(res => res.json())
      .then(data => { if (data && data.length > 0) setProducts(data); })
      .catch(() => {});
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

  const images = [case1Img, case2Img, case1Img, case2Img, case1Img, case2Img];

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
          {filtered.length === 0 ? (
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
                  image={images[index % images.length]}
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
