from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Category, Product, ProductVariant, Coupon, Order, OrderItem, Review


class UserSerializer(serializers.ModelSerializer):
    """Datos públicos del usuario autenticado (Clase 2 - Dev 1: Auth)."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id', 'is_staff']


class RegisterSerializer(serializers.ModelSerializer):
    """Registro de nuevos usuarios (Clase 2 - Dev 1: API login/registro)."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Este nombre de usuario ya está en uso."})
        if attrs.get('email') and User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Este email ya está registrado."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=0, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'model_name', 'color', 'material', 'sku', 'stock', 'price_override', 'price']
        extra_kwargs = {
            'product': {'required': False},
        }

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True
    )
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'base_price',
            'category', 'category_id', 'variants', 'reviews', 'average_rating',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0


class CouponSerializer(serializers.ModelSerializer):
    """CRUD de cupones para el admin (Clase 4 - Dev 1: API cupones de descuento)."""

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
    items = OrderItemSerializer(many=True)
    coupon_code = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'status', 'total_amount', 'items', 'coupon_code']
        read_only_fields = ['status', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        coupon_code = validated_data.pop('coupon_code', None)
        
        # Basic order creation without complex logic. 
        # The view handles checkout calculation, stock verification and MP integration.
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            # We will populate price_at_purchase in the checkout view
            OrderItem.objects.create(order=order, **item_data)
            
        return order


class OrderHistoryItemSerializer(serializers.ModelSerializer):
    """Detalle de un item dentro del historial de compras del usuario."""
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)
    variant_label = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'variant_label', 'quantity', 'price_at_purchase']

    def get_variant_label(self, obj):
        return f"{obj.product_variant.model_name} · {obj.product_variant.color}"


class OrderHistorySerializer(serializers.ModelSerializer):
    """Historial de compras del usuario (Clase 3 - Dev 2: gestión de órdenes)."""
    items = OrderHistoryItemSerializer(many=True, read_only=True)
    invoice_available = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_amount', 'created_at', 'updated_at',
            'items', 'invoice_available',
        ]

    def get_invoice_available(self, obj):
        # Solo hay factura una vez que el pago fue confirmado.
        return obj.status == 'PAID'
