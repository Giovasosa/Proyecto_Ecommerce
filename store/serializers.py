from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from .models import Category, Product, ProductVariant, Coupon, Order, OrderItem, Review


class CategorySerializer(serializers.ModelSerializer):
    """Serializa categorías para mostrar en el frontend."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductVariantSerializer(serializers.ModelSerializer):
    # El precio puede venir de price_override o del precio base del producto.
    price = serializers.DecimalField(max_digits=10, decimal_places=0, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'model_name', 'color', 'material', 'sku', 'stock', 'price']


class ReviewSerializer(serializers.ModelSerializer):
    # Mostramos nombre de usuario y nombre del producto para facilitar la UI.
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'product_name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'base_price', 'category', 'variants', 'reviews', 'average_rating']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'active']


class OrderItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantSerializer(read_only=True)
    product_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(), source='product_variant', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product_variant', 'product_variant_id', 'quantity', 'price_at_purchase']
        read_only_fields = ['price_at_purchase']


class OrderSerializer(serializers.ModelSerializer):
    # El cliente envía los items y un cupón opcional para crear la orden.
    items = OrderItemSerializer(many=True)
    coupon_code = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'status', 'total_amount', 'coupon_code', 'items', 'created_at']
        read_only_fields = ['status', 'total_amount', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        coupon_code = validated_data.pop('coupon_code', None)
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
                raise serializers.ValidationError({'coupon_code': 'Cupón inválido o expirado'})

        # Guardar la orden con usuario autenticado si existe.
        user = None
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user

        order = Order.objects.create(user=user, coupon=coupon, **validated_data)
        total_amount = 0

        for item_data in items_data:
            variant = item_data['product_variant']
            quantity = item_data['quantity']

            if variant.stock < quantity:
                raise serializers.ValidationError({'items': f'Stock insuficiente para {variant.product.name} ({variant.color})'})

            price = variant.price
            item_total = price * quantity
            total_amount += item_total

            # Guardar el precio actual en el momento de la compra.
            OrderItem.objects.create(order=order, **item_data, price_at_purchase=price)

        if coupon:
            if coupon.discount_type == 'percentage':
                total_amount -= (total_amount * coupon.discount_value / 100)
            else:
                total_amount -= coupon.discount_value
            total_amount = max(total_amount, 0)

        order.total_amount = total_amount
        order.save()
        return order


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user
