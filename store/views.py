from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status, filters, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import mercadopago

from .models import Category, Product, ProductVariant, Review, Coupon, Order, OrderItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
    CouponSerializer,
    OrderSerializer,
    OrderItemSerializer,
    RegisterSerializer,
    UserSerializer,
)


# Estas vistas controlan la API del backend de e-commerce.
# Aquí tenemos endpoints de productos, categorías, reseñas, cupones, órdenes y autenticación.
class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permisos personalizados para que solo el dueño pueda editar su propio recurso."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'user', None) == request.user
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'user', None) == request.user


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista y muestra categorías disponibles para el frontend."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista y filtra productos, con búsqueda y ordenación simple."""
    queryset = Product.objects.prefetch_related('variants', 'reviews').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name', 'variants__model_name', 'variants__color']
    ordering_fields = ['created_at', 'base_price', 'name']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            # Si viene el parámetro category, solo mostramos productos de esa categoría.
            queryset = queryset.filter(category__slug=category_slug)
        return queryset


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
    serializer_class = CouponSerializer
    permission_classes = [permissions.AllowAny]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__name', 'user__username', 'comment']

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product_variant__product').all()
        return Order.objects.prefetch_related('items__product_variant__product').filter(user=self.request.user)


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomAuthToken(TokenObtainPairView):
    """Endpoint de login que devuelve access y refresh tokens JWT con datos del usuario."""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            try:
                username = request.data.get('username')
                user = User.objects.get(username=username)
                response.data['user'] = UserSerializer(user).data
            except User.DoesNotExist:
                pass
        return response


class TokenRefreshAPIView(TokenRefreshView):
    """Endpoint para refrescar el access token usando el refresh token."""
    pass


class UserDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CheckoutAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    items_data = request.data.get('items', [])
                    if not items_data:
                        return Response({'error': 'El carrito está vacío'}, status=status.HTTP_400_BAD_REQUEST)

                    coupon_code = request.data.get('coupon_code')
                    coupon = None
                    if coupon_code:
                        try:
                            coupon = Coupon.objects.get(
                                code=coupon_code,
                                active=True,
                                valid_from__lte=timezone.now(),
                                valid_to__gte=timezone.now(),
                            )
                        except Coupon.DoesNotExist:
                            return Response({'error': 'Cupón inválido o expirado'}, status=status.HTTP_400_BAD_REQUEST)

                    order = Order(
                        user=request.user if request.user.is_authenticated else None,
                        first_name=serializer.validated_data['first_name'],
                        last_name=serializer.validated_data['last_name'],
                        email=serializer.validated_data['email'],
                        phone=serializer.validated_data['phone'],
                        address=serializer.validated_data['address'],
                        coupon=coupon,
                    )
                    order.save()

                    total_amount = 0

                    for item in items_data:
                        variant = ProductVariant.objects.select_for_update().get(id=item['product_variant_id'])
                        quantity = item['quantity']

                        if variant.stock < quantity:
                            raise ValueError(f'Stock insuficiente para {variant.product.name} ({variant.color})')

                        variant.stock -= quantity
                        variant.save()

                        price = variant.price
                        item_total = price * quantity
                        total_amount += item_total

                        OrderItem.objects.create(
                            order=order,
                            product_variant=variant,
                            quantity=quantity,
                            price_at_purchase=price,
                        )

                        mp_items.append({
                            'title': str(variant),
                            'quantity': quantity,
                            'unit_price': float(price),
                        })

                    if coupon:
                        if coupon.discount_type == 'percentage':
                            total_amount -= (total_amount * coupon.discount_value / 100)
                        else:
                            total_amount -= coupon.discount_value
                        total_amount = max(total_amount, 0)

                    order.total_amount = total_amount
                    order.save()

                    sdk = mercadopago.SDK(getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', 'TEST-TOKEN-AQUI'))
                    preference_data = {
                        'items': mp_items,
                        'payer': {
                            'name': order.first_name,
                            'surname': order.last_name,
                            'email': order.email,
                        },
                        'external_reference': str(order.id),
                        'back_urls': {
                            'success': 'http://localhost:3000/success',
                            'failure': 'http://localhost:3000/failure',
                            'pending': 'http://localhost:3000/pending',
                        },
                        'auto_return': 'approved',
                    }
                    preference_response = sdk.preference().create(preference_data)
                    if preference_response['status'] != 201:
                        raise Exception('Error al crear preferencia en MercadoPago')

                    preference = preference_response['response']
                    return Response({
                        'order_id': order.id,
                        'init_point': preference['init_point'],
                        'sandbox_init_point': preference.get('sandbox_init_point', ''),
                    }, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': 'Ocurrió un error al procesar el pago', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        topic = request.query_params.get('topic') or request.query_params.get('type')
        payment_id = request.query_params.get('id') or request.data.get('data', {}).get('id')

# =============================================================================
# Sales Report API — Solo Admin
# =============================================================================

class SalesReportAPIView(APIView):
    """
    GET /api/reports/sales/
    Parámetros:
    - period: daily|weekly|monthly (default: daily)
    - date_from: YYYY-MM-DD (default: 30 días atrás)
    - date_to: YYYY-MM-DD (default: hoy)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Parámetros
        period = request.query_params.get('period', 'daily')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        now = timezone.now()
        if date_from:
            try:
                sdk = mercadopago.SDK(getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', 'TEST-TOKEN-AQUI'))
                payment_info = sdk.payment().get(payment_id)
                if payment_info['status'] == 200:
                    payment = payment_info['response']
                    if payment['status'] == 'approved':
                        order_id = payment['external_reference']
                        try:
                            order = Order.objects.get(id=order_id)
                            if order.status != 'PAID':
                                order.status = 'PAID'
                                order.mercadopago_payment_id = payment_id
                                order.save()
                                from .utils import generate_invoice_pdf
                                try:
                                    generate_invoice_pdf(order)
                                except Exception as e:
                                    print(f'Error generando PDF para la orden {order.id}: {e}')
                        except Order.DoesNotExist:
                            pass
            except Exception as e:
                print(f'Error procesando webhook: {e}')

        return Response(status=status.HTTP_200_OK)
