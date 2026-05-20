from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Product, ProductVariant, Review, Coupon, Order, OrderItem
from .serializers import ProductSerializer, ReviewSerializer, OrderSerializer
import mercadopago
from django.conf import settings

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        # Asumiendo que requieres autenticación para dejar reseñas.
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # En caso de permitir reseñas anónimas, tendrías que modificar el modelo.
            pass

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
