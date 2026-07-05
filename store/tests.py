from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import Category, Product, ProductVariant, Order, OrderItem, Review

class StoreIntegrationTests(APITestCase):
    
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='testpassword123')
        self.user2 = User.objects.create_user(username='user2', password='testpassword123')
        
        # Create products and variants
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product', 
            slug='test-product', 
            base_price=50000, 
            category=self.category
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            model_name='Model X',
            color='Black',
            sku='TEST-SKU-01',
            stock=10
        )
        
        # Authenticate user1
        self.client.force_authenticate(user=self.user1)
        
    def test_checkout_updates_stock(self):
        """Test that completing a checkout reduces the stock automatically"""
        initial_stock = self.variant.stock
        
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            "email": "juan@test.com",
            "phone": "0987654321",
            "address": "Calle Falsa 123",
            "items": [
                {
                    "product_variant_id": self.variant.id,
                    "quantity": 2
                }
            ]
        }
        
        response = self.client.post(reverse('checkout'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Reload variant and check stock
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, initial_stock - 2)
        
    def test_order_cancellation_restores_stock(self):
        """Test that cancelling an order restores the variant stock"""
        # First create order
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            "email": "juan@test.com",
            "phone": "0987654321",
            "address": "Calle Falsa 123",
            "items": [
                {
                    "product_variant_id": self.variant.id,
                    "quantity": 3
                }
            ]
        }
        response = self.client.post(reverse('checkout'), data, format='json')
        order_id = response.data['order_id']
        
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 7) # 10 - 3
        
        # Cancel order
        cancel_url = reverse('order-cancel', kwargs={'pk': order_id})
        cancel_response = self.client.post(cancel_url)
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        
        # Verify stock restored
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 10)
        
    def test_my_orders_history(self):
        """Test that user can see their order history"""
        # Create an order
        order = Order.objects.create(
            user=self.user1,
            first_name='Test',
            last_name='User',
            email='test@user.com'
        )
        OrderItem.objects.create(
            order=order,
            product_variant=self.variant,
            quantity=1,
            price_at_purchase=50000
        )
        
        response = self.client.get(reverse('order-my-orders'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order.id)
        
    def test_review_requires_purchase(self):
        """Test that a user cannot leave a review if they haven't purchased the product"""
        review_data = {
            "product": self.product.id,
            "rating": 5,
            "comment": "Great product!"
        }
        # Try to review without buying
        response = self.client.post(reverse('review-list'), review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Solo puedes dejar reseñas en productos que hayas comprado.", str(response.data))
        
        # Now create a paid order for user1
        order = Order.objects.create(
            user=self.user1,
            status='PAID',
            first_name='Test',
            last_name='User',
            email='test@user.com'
        )
        OrderItem.objects.create(
            order=order,
            product_variant=self.variant,
            quantity=1,
            price_at_purchase=50000
        )
        
        # Try to review again
        response_success = self.client.post(reverse('review-list'), review_data, format='json')
        self.assertEqual(response_success.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_success.data['rating'], 5)
