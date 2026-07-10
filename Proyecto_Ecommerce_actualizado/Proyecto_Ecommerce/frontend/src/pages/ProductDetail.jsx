import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Star, ChevronLeft } from 'lucide-react';
import { useCart } from '../context/CartContext';
import case1Img from '../assets/case1.png';
import './ProductDetail.css';

const mockProduct = {
  id: 1,
  name: "Obsidian Dark Silicone",
  description: "La funda definitiva para proteger tu smartphone con un estilo sobrio y elegante. Material de silicona líquida premium que ofrece un agarre perfecto y protección contra caídas extremas.",
  base_price: "120000",
  category: { name: "Silicone Premium" },
  average_rating: 4.5,
  variants: [
    { id: 101, model_name: "iPhone 15 Pro", color: "Dark Purple", material: "Silicone", stock: 15, price: 120000 },
    { id: 102, model_name: "iPhone 15 Pro Max", color: "Midnight Black", material: "Silicone", stock: 0, price: 125000 }
  ],
  reviews: [
    { id: 1, user_name: "admin", rating: 5, comment: "Excelente calidad, muy recomendada.", created_at: "2023-10-01" },
    { id: 2, user_name: "cliente", rating: 4, comment: "Me gusta mucho el color, aunque es un poco resbaladiza.", created_at: "2023-10-05" }
  ]
};

const ProductDetail = () => {
  const { id } = useParams();
  const { addToCart } = useCart();
  const [product, setProduct] = useState(null);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/products/${id}/`)
      .then(res => {
        if (!res.ok) throw new Error("Producto no encontrado");
        return res.json();
      })
      .then(data => {
        setProduct(data);
        if (data.variants && data.variants.length > 0) {
          setSelectedVariant(data.variants[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.log("Usando producto mock debido a error de red o backend vacío.");
        setProduct(mockProduct);
        setSelectedVariant(mockProduct.variants[0]);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div className="container" style={{paddingTop: '100px'}}>Cargando...</div>;
  if (!product) return <div className="container" style={{paddingTop: '100px'}}>Producto no encontrado.</div>;

  const handleAddToCart = () => {
    if (selectedVariant && selectedVariant.stock > 0) {
      addToCart(product, selectedVariant, 1);
    }
  };

  return (
    <div className="product-detail-page container">
      <div className="back-link">
        <Link to="/"><ChevronLeft size={20} /> Volver al catálogo</Link>
      </div>

      <div className="product-detail-grid">
        <div className="product-image-large glass-panel">
          <img src={case1Img} alt={product.name} />
        </div>

        <div className="product-info-panel">
          <span className="category-tag">{product.category?.name || "Premium"}</span>
          <h1>{product.name}</h1>
          
          <div className="product-rating">
            <div className="stars">
              {[1, 2, 3, 4, 5].map(star => (
                <Star 
                  key={star} 
                  size={18} 
                  fill={star <= Math.round(product.average_rating || 0) ? "var(--accent-color)" : "transparent"} 
                  color={star <= Math.round(product.average_rating || 0) ? "var(--accent-color)" : "var(--text-secondary)"} 
                />
              ))}
            </div>
            <span>({product.reviews?.length || 0} reseñas)</span>
          </div>

          <p className="product-price-large">Gs. {selectedVariant ? selectedVariant.price : product.base_price}</p>
          <p className="product-description">{product.description || "Protección Premium para tu dispositivo."}</p>

          <div className="variants-section">
            <h3>Selecciona tu modelo:</h3>
            <div className="variants-grid">
              {product.variants?.map(variant => (
                <button 
                  key={variant.id}
                  className={`variant-btn glass-panel ${selectedVariant?.id === variant.id ? 'active' : ''} ${variant.stock === 0 ? 'disabled' : ''}`}
                  onClick={() => setSelectedVariant(variant)}
                  disabled={variant.stock === 0}
                >
                  <span className="variant-model">{variant.model_name}</span>
                  <span className="variant-color">{variant.color}</span>
                  {variant.stock === 0 && <span className="out-of-stock">Agotado</span>}
                </button>
              ))}
            </div>
          </div>

          <button 
            className="btn-primary add-to-cart-large"
            onClick={handleAddToCart}
            disabled={!selectedVariant || selectedVariant.stock === 0}
          >
            {selectedVariant?.stock === 0 ? 'Sin Stock' : 'Añadir al Carrito'}
          </button>
        </div>
      </div>

      <div className="reviews-section">
        <h2>Reseñas de Clientes</h2>
        {product.reviews && product.reviews.length > 0 ? (
          <div className="reviews-list">
            {product.reviews.map(review => (
              <div key={review.id} className="review-card glass-panel">
                <div className="review-header">
                  <strong>{review.user_name}</strong>
                  <div className="stars">
                    {[1, 2, 3, 4, 5].map(star => (
                      <Star 
                        key={star} 
                        size={14} 
                        fill={star <= review.rating ? "var(--accent-color)" : "transparent"} 
                        color={star <= review.rating ? "var(--accent-color)" : "var(--text-secondary)"} 
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
  );
};

export default ProductDetail;
