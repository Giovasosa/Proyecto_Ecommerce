from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta

from .models import Category, Product, ProductVariant, Review, Coupon, Order, OrderItem
from .serializers import (
    CategorySerializer,
    ProductSerializer, ProductListSerializer, ProductWriteSerializer,
    ProductVariantSerializer, ProductVariantWriteSerializer,
    ReviewSerializer, ReviewStatsSerializer,
    OrderSerializer, OrderListSerializer, OrderDetailSerializer, OrderStatusUpdateSerializer,
    OrderItemSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsAdminUser
from django.conf import settings


# =============================================================================
# Category ViewSet
# =============================================================================

class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD completo de categorías. Solo admin puede crear/editar/eliminar."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# =============================================================================
# Product ViewSet — CRUD con filtros y búsqueda
# =============================================================================

class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de productos.
    - GET: Cualquier usuario (solo productos activos por defecto)
    - POST/PUT/DELETE: Solo admin/staff
    - Filtros: ?category=slug, ?min_price=X, ?max_price=Y, ?search=texto
    - Ordenamiento: ?ordering=base_price, -base_price, name, -created_at
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'variants__model_name']
    ordering_fields = ['base_price', 'name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related(
            'variants', 'reviews', 'reviews__user'
        )

        # Admins ven todos los productos, usuarios normales solo activos
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)

        # Filtro por categoría (slug)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Filtro por rango de precio
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)

        # Filtro por stock disponible
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(variants__stock__gt=0).distinct()

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        return ProductSerializer

    # --- Acciones de variantes como sub-recurso ---

    @action(detail=True, methods=['get', 'post'], url_path='variants')
    def variants(self, request, pk=None):
        """
        GET /api/products/{id}/variants/ — Lista variantes del producto
        POST /api/products/{id}/variants/ — Crea variante (admin)
        """
        product = self.get_object()

        if request.method == 'GET':
            variants = product.variants.all()
            if not (request.user and request.user.is_staff):
                variants = variants.filter(is_active=True)
            serializer = ProductVariantSerializer(variants, many=True)
            return Response(serializer.data)

        # POST — Solo admin
        if not (request.user and request.user.is_staff):
            return Response(
                {"error": "Solo administradores pueden crear variantes."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductVariantWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch', 'delete'],
            url_path='variants/(?P<variant_id>[0-9]+)')
    def variant_detail(self, request, pk=None, variant_id=None):
        """
        PUT/PATCH /api/products/{id}/variants/{variant_id}/ — Edita variante (admin)
        DELETE /api/products/{id}/variants/{variant_id}/ — Elimina variante (admin)
        """
        product = self.get_object()

        if not (request.user and request.user.is_staff):
            return Response(
                {"error": "Solo administradores pueden modificar variantes."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            variant = product.variants.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response(
                {"error": "Variante no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'DELETE':
            variant.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # PUT o PATCH
        partial = request.method == 'PATCH'
        serializer = ProductVariantWriteSerializer(variant, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='review-stats')
    def review_stats(self, request, pk=None):
        """GET /api/products/{id}/review-stats/ — Estadísticas de reseñas."""
        product = self.get_object()
        reviews = product.reviews.all()

        stats = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        stats['average_rating'] = round(stats['average_rating'] or 0, 1)

        # Distribución por estrella
        distribution = {}
        for i in range(1, 6):
            distribution[str(i)] = reviews.filter(rating=i).count()
        stats['distribution'] = distribution

        serializer = ReviewStatsSerializer(stats)
        return Response(serializer.data)


# =============================================================================
# Review ViewSet
# =============================================================================

class ReviewViewSet(viewsets.ModelViewSet):
    """
    Sistema de reseñas con validación de compra.
    - Solo usuarios autenticados pueden crear reseñas
    - Un usuario solo puede dejar una reseña por producto
    - Solo el autor puede editar/eliminar su reseña
    - Filtro: ?product=id
    """
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer

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


# =============================================================================
# Order ViewSet — Gestión de órdenes
# =============================================================================

class OrderViewSet(viewsets.ModelViewSet):
    """
    Gestión de órdenes.
    - Admin: ve todas las órdenes, puede cambiar estado
    - Usuario autenticado: ve solo sus órdenes
    - my-orders: historial del usuario
    - cancel: cancela orden pendiente
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.select_related('user', 'coupon').prefetch_related(
            'items', 'items__product_variant', 'items__product_variant__product'
        )

        if user.is_staff:
            # Admin ve todas
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
        else:
            # Usuario normal ve solo las suyas
            queryset = queryset.filter(user=user)

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        if self.action in ['partial_update', 'update']:
            return OrderStatusUpdateSerializer
        return OrderDetailSerializer

    def update(self, request, *args, **kwargs):
        """Solo admin puede actualizar estado de órdenes."""
        if not request.user.is_staff:
            return Response(
                {"error": "Solo administradores pueden cambiar el estado de una orden."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Solo admin puede actualizar estado de órdenes."""
        if not request.user.is_staff:
            return Response(
                {"error": "Solo administradores pueden cambiar el estado de una orden."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='my-orders')
    def my_orders(self, request):
        """GET /api/orders/my-orders/ — Historial de compras del usuario."""
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        POST /api/orders/{id}/cancel/ — Cancela una orden pendiente.
        El signal pre_save restaurará el stock automáticamente.
        """
        order = self.get_object()

        # Solo el dueño o un admin pueden cancelar
        if not request.user.is_staff and order.user != request.user:
            return Response(
                {"error": "No tienes permiso para cancelar esta orden."},
                status=status.HTTP_403_FORBIDDEN
            )

        if order.status != 'PENDING':
            return Response(
                {"error": f"Solo se pueden cancelar órdenes pendientes. Estado actual: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # El signal pre_save se encargará de restaurar el stock
        order.status = 'CANCELLED'
        order.save()

        return Response(
            {"message": "Orden cancelada exitosamente. El stock ha sido restaurado."},
            status=status.HTTP_200_OK
        )


# =============================================================================
# Checkout (existente, mantenido)
# =============================================================================

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

                    # Aplicar descuento
                    if coupon:
                        if coupon.discount_type == 'percentage':
                            total_amount -= (total_amount * coupon.discount_value / 100)
                        else:
                            total_amount -= coupon.discount_value

                        total_amount = max(total_amount, 0)

                    order.total_amount = total_amount
                    order.save()

                    # Respuesta para pago por transferencia o efectivo
                    payment_info = {
                        "TRANSFER": "Por favor, realiza la transferencia bancaria al número de cuenta proporcionado y envía el comprobante.",
                        "CASH": "Por favor, paga en efectivo al momento de recibir el producto o en la sucursal."
                    }

                    return Response({
                        "message": "Orden creada exitosamente",
                        "order_id": order.id,
                        "payment_method": order.payment_method,
                        "payment_instructions": payment_info.get(order.payment_method, ""),
                    }, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": "Ocurrió un error al procesar el checkout", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                from datetime import datetime
                date_from = timezone.make_aware(datetime.strptime(date_from, '%Y-%m-%d'))
            except ValueError:
                return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}, status=400)
        else:
            date_from = now - timedelta(days=30)

        if date_to:
            try:
                from datetime import datetime
                date_to = timezone.make_aware(datetime.strptime(date_to, '%Y-%m-%d').replace(
                    hour=23, minute=59, second=59
                ))
            except ValueError:
                return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}, status=400)
        else:
            date_to = now

        # Órdenes pagadas en el rango
        paid_orders = Order.objects.filter(
            status='PAID',
            created_at__gte=date_from,
            created_at__lte=date_to
        )

        # --- Resumen general ---
        summary = paid_orders.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
            average_ticket=Avg('total_amount')
        )
        summary['total_revenue'] = summary['total_revenue'] or 0
        summary['total_orders'] = summary['total_orders'] or 0
        summary['average_ticket'] = round(summary['average_ticket'] or 0, 0)

        # --- Ventas por período ---
        trunc_func = {
            'daily': TruncDay,
            'weekly': TruncWeek,
            'monthly': TruncMonth,
        }.get(period, TruncDay)

        sales_by_period = paid_orders.annotate(
            period=trunc_func('created_at')
        ).values('period').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('period')

        # Formatear fechas
        sales_timeline = [
            {
                'period': entry['period'].strftime('%Y-%m-%d'),
                'revenue': float(entry['revenue'] or 0),
                'orders': entry['orders']
            }
            for entry in sales_by_period
        ]

        # --- Top 10 productos más vendidos ---
        top_products = OrderItem.objects.filter(
            order__status='PAID',
            order__created_at__gte=date_from,
            order__created_at__lte=date_to
        ).values(
            product_name=F('product_variant__product__name')
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price_at_purchase'))
        ).order_by('-total_sold')[:10]

        # --- Ingresos por categoría ---
        revenue_by_category = OrderItem.objects.filter(
            order__status='PAID',
            order__created_at__gte=date_from,
            order__created_at__lte=date_to
        ).values(
            category_name=F('product_variant__product__category__name')
        ).annotate(
            total_revenue=Sum(F('quantity') * F('price_at_purchase')),
            total_items=Sum('quantity')
        ).order_by('-total_revenue')

        # --- Órdenes por estado (todas, no solo pagadas) ---
        all_orders = Order.objects.filter(
            created_at__gte=date_from,
            created_at__lte=date_to
        )
        orders_by_status = dict(
            all_orders.values_list('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        return Response({
            'date_range': {
                'from': date_from.strftime('%Y-%m-%d'),
                'to': date_to.strftime('%Y-%m-%d'),
                'period': period
            },
            'summary': {
                'total_revenue': float(summary['total_revenue']),
                'total_orders': summary['total_orders'],
                'average_ticket': float(summary['average_ticket'])
            },
            'sales_timeline': sales_timeline,
            'top_products': list(top_products),
            'revenue_by_category': list(revenue_by_category),
            'orders_by_status': orders_by_status
        })


# =============================================================================
# Stock Report API — Solo Admin
# =============================================================================

class StockReportAPIView(APIView):
    """
    GET /api/reports/stock/
    Reporte de inventario con alertas de stock bajo.
    Parámetros:
    - low_stock_threshold: número (default: 5)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        threshold = int(request.query_params.get('low_stock_threshold', 5))

        # Variantes con stock bajo
        low_stock = ProductVariant.objects.filter(
            stock__lte=threshold,
            is_active=True
        ).select_related('product').values(
            'id', 'sku',
            product_name=F('product__name'),
            variant_name=F('model_name'),
            color=F('color'),
            current_stock=F('stock')
        ).order_by('stock')

        # Variantes sin stock
        out_of_stock = ProductVariant.objects.filter(
            stock=0,
            is_active=True
        ).count()

        # Resumen general de inventario
        total_variants = ProductVariant.objects.filter(is_active=True).count()
        total_stock_units = ProductVariant.objects.filter(
            is_active=True
        ).aggregate(total=Sum('stock'))['total'] or 0

        # Stock por categoría
        stock_by_category = ProductVariant.objects.filter(
            is_active=True
        ).values(
            category_name=F('product__category__name')
        ).annotate(
            total_stock=Sum('stock'),
            variant_count=Count('id')
        ).order_by('-total_stock')

        return Response({
            'summary': {
                'total_active_variants': total_variants,
                'total_stock_units': total_stock_units,
                'out_of_stock_count': out_of_stock,
                'low_stock_count': len(low_stock),
                'low_stock_threshold': threshold
            },
            'low_stock_items': list(low_stock),
            'stock_by_category': list(stock_by_category)
        })
