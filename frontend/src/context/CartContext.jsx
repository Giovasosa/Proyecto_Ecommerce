import React, { createContext, useState, useContext } from 'react';
import { toast } from 'sonner';

const CartContext = createContext();

export const useCart = () => useContext(CartContext);

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const addToCart = React.useCallback((product, variant, quantity = 1) => {
    setCartItems(prev => {
      const existing = prev.find(item => item.variant.id === variant.id);
      if (existing) {
        return prev.map(item => 
          item.variant.id === variant.id 
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      }
      return [...prev, { product, variant, quantity }];
    });
    setIsCartOpen(true);
    toast.success(`${product.name} añadido al carrito`);
  }, []);

  const removeFromCart = React.useCallback((variantId) => {
    setCartItems(prev => prev.filter(item => item.variant.id !== variantId));
  }, []);

  const toggleCart = React.useCallback(() => {
    setIsCartOpen(prev => !prev);
  }, []);

  const clearCart = React.useCallback(() => {
    setCartItems([]);
  }, []);

  const cartTotal = cartItems.reduce((total, item) => total + (item.variant.price * item.quantity), 0);
  const cartCount = cartItems.reduce((count, item) => count + item.quantity, 0);

  return (
    <CartContext.Provider value={{ 
      cartItems, addToCart, removeFromCart, clearCart,
      isCartOpen, toggleCart, cartTotal, cartCount 
    }}>
      {children}
    </CartContext.Provider>
  );
};
