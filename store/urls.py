from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ReviewViewSet,
    CouponViewSet,
    OrderViewSet,
    RegisterAPIView,
    CustomAuthToken,
    UserDetailAPIView,
    CheckoutAPIView,
    PaymentWebhookView,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', CustomAuthToken.as_view(), name='login'),
    path('auth/me/', UserDetailAPIView.as_view(), name='user-detail'),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('webhook/', PaymentWebhookView.as_view(), name='webhook'),
]
