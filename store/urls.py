from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ReviewViewSet,
    CouponViewSet,
    OrderViewSet,
    RegisterAPIView,
    CustomAuthToken,
    TokenRefreshAPIView,
    UserDetailAPIView,
    CheckoutAPIView,
    PaymentWebhookView,
    SalesReportAPIView,
    # StockReportAPIView,
)

# Rutas principales del backend de la tienda.
# El router maneja los recursos REST básicos y las vistas específicas se agregan abajo.
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', CustomAuthToken.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshAPIView.as_view(), name='token_refresh'),
    path('auth/me/', UserDetailAPIView.as_view(), name='user-detail'),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('reports/sales/', SalesReportAPIView.as_view(), name='sales-report'),
    # path('reports/stock/', StockReportAPIView.as_view(), name='stock-report'),
]
