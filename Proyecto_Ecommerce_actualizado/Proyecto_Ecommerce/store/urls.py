from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ProductViewSet, ProductVariantViewSet, CategoryViewSet, CouponViewSet,
    ReviewViewSet, MyOrdersViewSet,
    CheckoutAPIView, PaymentWebhookView, InvoiceDownloadView,
    RegisterView, LoginView, MeView, SalesReportView,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'variants', ProductVariantViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'orders', MyOrdersViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),

    # Autenticación (Clase 2 - Dev 1)
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='login-refresh'),
    path('auth/me/', MeView.as_view(), name='me'),

    # Pagos y órdenes (Clase 3)
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('webhook/', PaymentWebhookView.as_view(), name='webhook'),
    path('orders/<int:order_id>/invoice/', InvoiceDownloadView.as_view(), name='order-invoice'),

    # Reportes (Clase 4 - Dev 2)
    path('reports/sales/', SalesReportView.as_view(), name='sales-report'),
]
