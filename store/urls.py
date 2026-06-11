from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ReviewViewSet,
    OrderViewSet,
    CheckoutAPIView,
    SalesReportAPIView,
    StockReportAPIView,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ReviewViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('reports/sales/', SalesReportAPIView.as_view(), name='sales-report'),
    path('reports/stock/', StockReportAPIView.as_view(), name='stock-report'),
]
