import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Star, ChevronLeft, ShoppingBag, Shield, Truck, RotateCcw } from 'lucide-react';
import { useCart } from '../context/CartContext';
import case1Img from '../assets/case1.png';
import PageTransition from '../components/PageTransition';
import './ProductDetail.css';

const ProductDetail = () => {
  const { id } = useParams();
  const { addToCart } = useCart();
  const [product, setProduct] = useState(null);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [added, setAdded] = useState(false);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/products/${id}/`)
      .then(res => { if (!res.ok) throw new Error(); return res.json(); })
      .then(data => {
        setProduct(data);
        if (data.variants?.length > 0) setSelectedVariant(data.variants[0]);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [id]);

  const handleAddToCart = () => {
    if (selectedVariant && selectedVariant.stock > 0) {
      addToCart(product, selectedVariant, 1);
      setAdded(true);
      setTimeout(() => setAdded(false), 2000);
    }
  };

  if (loading) return (
    <div className="container detail-loading">
      <div className="loading-skeleton" />
    </div>
  );

  if (error || !product) return (
    <div className="container" style={{ paddingTop: '100px', textAlign: 'center' }}>
      <p>Producto no encontrado o error de conexión.</p>
      <Link to="/catalogo" className="btn-secondary" style={{ marginTop: 16, display: 'inline-block' }}>Volver al catálogo</Link>
    </div>
  );

  return (
    <PageTransition>
    <div className="product-detail-page">
      <div className="container">
        {/* Breadcrumb */}
        <div className="back-link">
          <Link to="/catalogo">
            <ChevronLeft size={18} /> Volver al catálogo
          </Link>
        </div>

        <div className="product-detail-grid">
          {/* IMAGE */}
          <div className="product-image-section">
            <div className="product-image-large">
              <img src={product.image || case1Img} alt={product.name} />
            </div>
            <div className="product-badges">
              <span className="badge"><Shield size={14} /> Protección garantizada</span>
              <span className="badge"><Truck size={14} /> Envío 24hs</span>
              <span className="badge"><RotateCcw size={14} /> Cambios sin cargo</span>
            </div>
          </div>

          {/* INFO */}
          <div className="product-info-panel">
            <span className="category-tag">{product.category?.name || 'Premium'}</span>
            <h1>{product.name}</h1>

            <div className="product-rating">
              <div className="stars">
                {[1,2,3,4,5].map(s => (
                  <Star key={s} size={16}
                    fill={s <= Math.round(product.average_rating || 0) ? '#0a0a0a' : 'transparent'}
                    color={s <= Math.round(product.average_rating || 0) ? '#0a0a0a' : '#d0d0d0'}
                  />
                ))}
              </div>
              <span>({product.reviews?.length || 0} reseñas)</span>
            </div>

            <p className="product-price-large">
              Gs. {(selectedVariant?.price || product.base_price).toLocaleString('es-PY')}
            </p>

            <p className="product-description">{product.description}</p>

            <div className="variants-section">
              <h3>Seleccioná tu modelo</h3>
              <div className="variants-grid">
                {product.variants?.map(variant => (
                  <button
                    key={variant.id}
                    className={`variant-btn ${selectedVariant?.id === variant.id ? 'active' : ''} ${variant.stock === 0 ? 'disabled' : ''}`}
                    onClick={() => variant.stock > 0 && setSelectedVariant(variant)}
                    disabled={variant.stock === 0}
                  >
                    <span className="variant-model">{variant.model_name}</span>
                    <span className="variant-color">{variant.color}</span>
                    {variant.stock === 0 && <span className="out-of-stock">Agotado</span>}
                    {variant.stock > 0 && variant.stock <= 5 && (
                      <span className="low-stock">¡Solo {variant.stock}!</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            <button
              className={`btn-primary add-to-cart-large ${added ? 'added' : ''}`}
              onClick={handleAddToCart}
              disabled={!selectedVariant || selectedVariant.stock === 0}
            >
              <ShoppingBag size={18} style={{ marginRight: 10 }} />
              {added ? '¡Agregado! ✓' : selectedVariant?.stock === 0 ? 'Sin Stock' : 'Añadir al Carrito'}
            </button>

            <div className="product-meta-info">
              <div className="meta-item">
                <span className="meta-label">Material</span>
                <span className="meta-value">{selectedVariant?.material || '—'}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">SKU</span>
                <span className="meta-value">{selectedVariant?.sku || `KR-${selectedVariant?.id}`}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Stock</span>
                <span className="meta-value">{selectedVariant?.stock ? `${selectedVariant.stock} unidades` : 'Agotado'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* REVIEWS */}
        <div className="reviews-section">
          <h2>Reseñas de Clientes</h2>
          {product.reviews?.length > 0 ? (
            <div className="reviews-list">
              {product.reviews.map(review => (
                <div key={review.id} className="review-card">
                  <div className="review-header">
                    <div>
                      <strong>{review.user_name}</strong>
                      <span className="review-date">{new Date(review.created_at).toLocaleDateString('es-PY', { year: 'numeric', month: 'long' })}</span>
                    </div>
                    <div className="stars">
                      {[1,2,3,4,5].map(s => (
                        <Star key={s} size={13}
                          fill={s <= review.rating ? '#0a0a0a' : 'transparent'}
                          color={s <= review.rating ? '#0a0a0a' : '#d0d0d0'}
                        />
                      ))}
                    </div>
                  </div>
                  <p className="review-comment">"{review.comment}"</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-reviews">Aún no hay reseñas para este producto.</p>
          )}
        </div>
      </div>
    </div>
    </PageTransition>
  );
};

export default ProductDetail;
