import React from 'react';
import { ShoppingCart } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import './ProductCard.css';

const ProductCard = ({ product, image }) => {
  const { addToCart } = useCart();

  const defaultVariant = product.variants && product.variants.length > 0 ? product.variants[0] : null;

  const handleAddToCart = (e) => {
    e.preventDefault(); // Evitar que el click navegue al link
    if (defaultVariant) {
      addToCart(product, defaultVariant, 1);
    } else {
      alert("Este producto no tiene variantes configuradas.");
    }
  };

  return (
    <Link to={`/product/${product.id}`} className="product-card glass-panel">
      <div className="card-image-container">
        <img src={image} alt={product.name} className="product-image" />
        <div className="card-actions">
          <button className="btn-icon" onClick={handleAddToCart} title="Agregar rápido">
            <ShoppingCart size={18} />
          </button>
        </div>
      </div>
      <div className="card-info">
        <span className="category-tag">{product.category?.name || "Premium"}</span>
        <h3 className="product-title">{product.name}</h3>
        <p className="product-price">Gs. {product.base_price}</p>
      </div>
    </Link>
  );
};

export default ProductCard;
