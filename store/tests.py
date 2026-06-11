from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Product, ProductVariant


class BackendApiTests(APITestCase):
    def setUp(self):
        # Creo una categoría y un producto de ejemplo para las pruebas.
        self.category = Category.objects.create(name='Celulares', slug='celulares')
        self.product = Product.objects.create(
            category=self.category,
            name='Teléfono de prueba',
            slug='telefono-de-prueba',
            description='Descripción de prueba',
            base_price=1000000,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            model_name='Modelo A',
            color='Negro',
            material='Plástico',
            sku='TESTSKU',
            stock=10,
        )

    def test_product_list_is_available(self):
        # Verifico que la lista de productos devuelva datos y esté disponible.
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    def test_user_registration_and_login(self):
        # Registro un usuario nuevo y luego me autentico con él.
        register_url = reverse('register')
        response = self.client.post(register_url, {
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'password123',
            'password2': 'password123',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        login_url = reverse('login')
        response = self.client.post(login_url, {
            'username': 'tester',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_category_filter_works(self):
        # Testeo el filtro por categoría en la lista de productos.
        url = reverse('product-list') + '?category=celulares'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
