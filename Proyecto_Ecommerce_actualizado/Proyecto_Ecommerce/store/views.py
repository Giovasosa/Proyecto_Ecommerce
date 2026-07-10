import os
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Count, F
from django.http import FileResponse, Http404
from django.utils import timezone
from django.utils.dateparse import parse_date

from rest_framework import viewsets, status, generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product, ProductVariant, Review, Coupon, Order, OrderItem
from .serializers import (
    CategorySerializer, ProductSerializer, ProductVariantSerializer,
    ReviewSerializer, CouponSerializer, OrderSerializer, OrderHistorySerializer,
    RegisterSerializer, UserSerializer,
)
from .permissions import IsAdminOrReadOnly
import mercadopago
from django.conf import settings

# ---------------------------------------------------------------------------
# Autenticación (Clase 2 - Dev 1: API login/registro, JWT tokens)
# ---------------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/  ->  crea un usuario nuevo (sin login automático)."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/  ->  devuelve access + refresh tokens (JWT)."""
    permission_classes = [AllowAny]


class MeView(APIView):
    """GET /api/auth/me/  ->  datos del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ---------------------------------------------------------------------------
# Catálogo (Clase 2 - Dev 2: CRUD productos + variantes, stock, filtros)
# ---------------------------------------------------------------------------

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de productos (solo admin puede escribir).
    Filtros: ?category=<id>&min_price=&max_price=
    Búsqueda: ?search=texto (nombre y descripción)
    Orden: ?ordering=base_price o -created_at
    """
    queryset = Product.objects.all().select_related('category').prefetch_related('variants', 'reviews')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['base_price', 'created_at', 'name']

    def get_queryset(self):
        qs = super().get_queryset()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            qs = qs.filter(base_price__gte=min_price)
        if max_price:
            qs = qs.filter(base_price__lte=max_price)
        return qs


class ProductVariantViewSet(viewsets.ModelViewSet):
    """CRUD de variantes (manejo de stock) — solo admin puede escribir."""
    queryset = ProductVariant.objects.all().select_related('product')
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'stock']
    search_fields = ['model_name', 'color', 'sku']


class CouponViewSet(viewsets.ModelViewSet):
    """CRUD de cupones (Clase 4 - Dev 1). Solo admin puede leer y escribir."""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------------------------
# Historial de compras (Clase 3 - Dev 2)
# ---------------------------------------------------------------------------

class MyOrdersViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/orders/  y  /api/orders/<id>/  ->  pedidos del usuario autenticado."""
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related('items__product_variant__product')
            .order_by('-created_at')
        )


# ---------------------------------------------------------------------------
# Factura en PDF (Clase 4 - Dev 1: Generar facturas PDF)
# ---------------------------------------------------------------------------

class InvoiceDownloadView(APIView):
    """
    GET /api/orders/<id>/invoice/
    Genera (si no existe) y devuelve el PDF de la factura de una orden pagada.
    Solo el dueño de la orden o un admin pueden descargarla.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise Http404("Orden no encontrada")

        if not request.user.is_staff and order.user_id != request.user.id:
            return Response({"error": "No tenés permiso para ver esta factura"}, status=status.HTTP_403_FORBIDDEN)

        if order.status != 'PAID':
            return Response(
                {"error": "La factura solo está disponible una vez confirmado el pago"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from .utils import generate_invoice_pdf

        pdf_filename = f"invoice_order_{order.id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'invoices', pdf_filename)

        if not os.path.exists(pdf_path):
            pdf_path = generate_invoice_pdf(order)

        return FileResponse(
            open(pdf_path, 'rb'),
            as_attachment=True,
            filename=pdf_filename,
            content_type='application/pdf',
        )


# ---------------------------------------------------------------------------
# Reportes de ventas (Clase 4 - Dev 2)
# ---------------------------------------------------------------------------

class SalesReportView(APIView):
    """
    GET /api/reports/sales/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    Solo admin. Resumen de ventas: totales, por día y productos más vendidos.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        paid_orders = Order.objects.filter(status='PAID')

        date_from = parse_date(request.query_params.get('date_from', '') or '')
        date_to = parse_date(request.query_params.get('date_to', '') or '')
        if date_from:
            paid_orders = paid_orders.filter(created_at__date__gte=date_from)
        if date_to:
            paid_orders = paid_orders.filter(created_at__date__lte=date_to)

        totals = paid_orders.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
        )

        sales_by_day = (
            paid_orders
            .extra(select={'day': "date(created_at)"})
            .values('day')
            .annotate(revenue=Sum('total_amount'), orders=Count('id'))
            .order_by('day')
        )

        top_products = (
            OrderItem.objects.filter(order__status='PAID', order__in=paid_orders)
            .values(
                product_name=F('product_variant__product__name'),
            )
            .annotate(
                units_sold=Sum('quantity'),
                revenue=Sum(F('price_at_purchase') * F('quantity')),
            )
            .order_by('-units_sold')[:10]
        )

        return Response({
            "total_revenue": totals['total_revenue'] or 0,
            "total_orders": totals['total_orders'] or 0,
            "sales_by_day": list(sales_by_day),
            "top_products": list(top_products),
        })

class CheckoutAPIView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    items_data = request.data.get('items', [])
                    if not items_data:
                        return Response({"error": "El carrito está vacío"}, status=status.HTTP_400_BAD_REQUEST)

                    coupon_code = request.data.get('coupon_code')
                    
                    # Validar cupón
                    coupon = None
                    if coupon_code:
                        try:
                            coupon = Coupon.objects.get(
                                code=coupon_code, 
                                active=True, 
                                valid_from__lte=timezone.now(), 
                                valid_to__gte=timezone.now()
                            )
                        except Coupon.DoesNotExist:
                            return Response({"error": "Cupón inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)

                    order = Order(
                        user=request.user if request.user.is_authenticated else None,
                        first_name=serializer.validated_data['first_name'],
                        last_name=serializer.validated_data['last_name'],
                        email=serializer.validated_data['email'],
                        phone=serializer.validated_data['phone'],
                        address=serializer.validated_data['address'],
                        coupon=coupon
                    )
                    order.save()

                    total_amount = 0
                    mp_items = []

                    for item in items_data:
                        # select_for_update() bloquea la fila hasta que termina la transacción,
                        # previniendo condiciones de carrera con el stock.
                        variant = ProductVariant.objects.select_for_update().get(id=item['product_variant_id'])
                        quantity = item['quantity']

                        if variant.stock < quantity:
                            raise ValueError(f"Stock insuficiente para {variant.product.name} ({variant.color})")
                        
                        variant.stock -= quantity
                        variant.save()

                        price = variant.price
                        item_total = price * quantity
                        total_amount += item_total

                        OrderItem.objects.create(
                            order=order,
                            product_variant=variant,
                            quantity=quantity,
                            price_at_purchase=price
                        )

                        mp_items.append({
                            "title": str(variant),
                            "quantity": quantity,
                            "unit_price": float(price)
                        })

                    # Aplicar descuento
                    if coupon:
                        if coupon.discount_type == 'percentage':
                            total_amount -= (total_amount * coupon.discount_value / 100)
                        else:
                            total_amount -= coupon.discount_value
                            
                        total_amount = max(total_amount, 0)
                    
                    order.total_amount = total_amount
                    order.save()

                    # Integración con MercadoPago
                    # NOTA: Debes agregar MERCADOPAGO_ACCESS_TOKEN a settings.py
                    sdk = mercadopago.SDK(getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', 'TEST-TOKEN-AQUI'))
                    
                    preference_data = {
                        "items": mp_items,
                        "payer": {
                            "name": order.first_name,
                            "surname": order.last_name,
                            "email": order.email,
                        },
                        "external_reference": str(order.id),
                        "back_urls": {
                            "success": "http://localhost:3000/success",
                            "failure": "http://localhost:3000/failure",
                            "pending": "http://localhost:3000/pending"
                        },
                        "auto_return": "approved"
                    }

                    preference_response = sdk.preference().create(preference_data)
                    
                    if preference_response["status"] != 201:
                        raise Exception("Error al crear preferencia en MercadoPago")

                    preference = preference_response["response"]
                    
                    return Response({
                        "order_id": order.id,
                        "init_point": preference['init_point'], # URL para redirigir al usuario en prod
                        "sandbox_init_point": preference.get('sandbox_init_point', '') # URL para pruebas
                    }, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": "Ocurrió un error al procesar el pago", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentWebhookView(APIView):
    def post(self, request):
        topic = request.query_params.get('topic') or request.query_params.get('type')
        payment_id = request.query_params.get('id') or request.data.get('data', {}).get('id')

        if topic == 'payment' and payment_id:
            try:
                sdk = mercadopago.SDK(getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', 'TEST-TOKEN-AQUI'))
                payment_info = sdk.payment().get(payment_id)
                
                if payment_info["status"] == 200:
                    payment = payment_info["response"]

                    if payment["status"] == "approved":
                        order_id = payment["external_reference"]
                        try:
                            order = Order.objects.get(id=order_id)
                            
                            if order.status != 'PAID':
                                order.status = 'PAID'
                                order.mercadopago_payment_id = payment_id
                                order.save()
                                
                                # Generar PDF
                                from .utils import generate_invoice_pdf
                                try:
                                    generate_invoice_pdf(order)
                                except Exception as e:
                                    print(f"Error generando PDF para la orden {order.id}: {e}")
                                    # TODO: Enviar email al cliente con la factura y al admin
                        except Order.DoesNotExist:
                            pass # Orden no encontrada, ignorar o loguear
            except Exception as e:
                print(f"Error procesando webhook: {e}")
                
        # MercadoPago espera un 200 OK para saber que recibimos la notificación correctamente
        return Response(status=status.HTTP_200_OK)
