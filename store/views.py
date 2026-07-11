from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

from rest_framework import viewsets, status, filters, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from django.http import FileResponse
import os
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
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
    ChangePasswordSerializer,
)


# Permiso simple: solo el dueño puede modificar su recurso (lectura abierta)
class IsOwnerOrReadOnly:
    from rest_framework.permissions import BasePermission

    class _Impl(BasePermission):
        def has_object_permission(self, request, view, obj):
            if request.method in ('GET', 'HEAD', 'OPTIONS'):
                return True
            return getattr(obj, 'user', None) == request.user

    def __call__(self):
        return IsOwnerOrReadOnly._Impl()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista y muestra categorías."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Productos con búsqueda y filtrado por categoría."""
    queryset = Product.objects.prefetch_related('variants', 'reviews').all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name', 'variants__model_name', 'variants__color']
    ordering_fields = ['created_at', 'base_price', 'name']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    # allow unauthenticated GETs

    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticatedOrReadOnly
        from rest_framework.permissions import AllowAny as _AllowAny
        if self.action in ['create']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()()]
        return [_AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product_variant__product').all()
        return Order.objects.prefetch_related('items__product_variant__product').filter(user=self.request.user)


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class CustomAuthToken(TokenObtainPairView):
    """Login que devuelve access y refresh tokens JWT + datos del usuario."""
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
    """Refresca tokens JWT."""
    pass


class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data.get("old_password")):
                return Response({"old_password": ["Contraseña actual incorrecta."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            return Response({"message": "Contraseña actualizada exitosamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
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
                    mp_items = []

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

                    # Fin del for items

                    if coupon:
                        if coupon.discount_type == 'percentage':
                            total_amount -= (total_amount * coupon.discount_value / 100)
                        else:
                            total_amount -= coupon.discount_value
                        total_amount = max(total_amount, 0)

                    order.total_amount = total_amount
                    order.save()

                    # --- Enviar correo de confirmación ---
                    email_subject = f'Confirmacion de Pedido #{order.id} - KR Cases'
                    email_body = f'Hola {order.first_name},\n\n'
                    email_body += f'¡Gracias por tu compra en KR Cases!\n\n'
                    email_body += f'Detalles de tu pedido (Referencia #{order.id}):\n'
                    for item in order.items.all():
                        email_body += f'- {item.quantity}x {item.product_variant.product.name} ({item.product_variant.color}): Gs. {item.price_at_purchase * item.quantity:,.0f}\n'
                    email_body += f'\nTotal: Gs. {order.total_amount:,.0f}\n'
                    email_body += f'Direccion de envio: {order.address}\n\n'
                    email_body += 'Nos pondremos en contacto contigo muy pronto para coordinar la entrega.\n\nSaludos,\nEl equipo de KR Cases'
                    
                    try:
                        send_mail(
                            email_subject,
                            email_body,
                            'ventas@krcases.com',
                            [order.email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        print(f"Error enviando correo: {e}")
                    # ------------------------------------

                    # Generar factura PDF de forma automática al finalizar el pedido
                    from .utils import generate_invoice_pdf
                    try:
                        generate_invoice_pdf(order)
                    except Exception as e:
                        print(f"Error generando PDF para la orden {order.id}: {e}")

                    return Response({
                        'order_id': order.id,
                        'message': 'Pedido recibido con éxito (Pago contra entrega)'
                    }, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': 'Ocurrió un error al procesar el pedido', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DownloadInvoiceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            # Solo el dueño de la orden o un admin puede descargarla
            if order.user != request.user and not request.user.is_staff:
                return Response({'error': 'No tienes permiso para ver esta factura.'}, status=status.HTTP_403_FORBIDDEN)
            
            pdf_filename = f"invoice_order_{order.id}.pdf"
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'invoices', pdf_filename)
            
            if not os.path.exists(pdf_path):
                # Si por alguna razon no existe, se intenta generar ahora
                from .utils import generate_invoice_pdf
                pdf_path = generate_invoice_pdf(order)
                
            return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        except Order.DoesNotExist:
            return Response({'error': 'Pedido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


# Reportes simples de ventas (solo admin)
class SalesReportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'daily')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        qs = Order.objects.filter(status='PAID')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        if period == 'daily':
            data = qs.annotate(day=TruncDay('created_at')).values('day').annotate(total=Sum('total_amount'), count=Count('id')).order_by('day')
        elif period == 'weekly':
            data = qs.annotate(week=TruncWeek('created_at')).values('week').annotate(total=Sum('total_amount'), count=Count('id')).order_by('week')
        else:
            data = qs.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total_amount'), count=Count('id')).order_by('month')

        return Response(list(data))


class StockReportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = ProductVariant.objects.select_related('product').values(
            'product__name',
            'color',
            'size',
        ).annotate(
            stock=Sum('stock')
        ).order_by('-stock')

        return Response(list(data))
