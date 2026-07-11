from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from django.db.models import Avg, Count, Q
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
        fields = ['id', 'product', 'model_name', 'color', 'material', 'sku',
                  'stock', 'price_override', 'price', 'is_active']
        read_only_fields = ['product']


class ProductVariantWriteSerializer(serializers.ModelSerializer):
    """Serializer de escritura para crear/editar variantes."""

    class Meta:
        model = ProductVariant
        fields = ['id', 'model_name', 'color', 'material', 'sku',
                  'stock', 'price_override', 'is_active']


# =============================================================================
# Review Serializers
# =============================================================================


class ReviewSerializer(serializers.ModelSerializer):
    # Mostramos nombre de usuario y nombre del producto para facilitar la UI.
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'product_name']


    def validate(self, data):
        """Valida que el usuario haya comprado el producto antes de dejar reseña."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            product = data.get('product')
            user = request.user

            if not user or not user.is_authenticated:
                raise serializers.ValidationError(
                    "Debes iniciar sesión para dejar una reseña."
                )

            # Verificar que el usuario compró el producto (orden PAID con variante del producto)
            has_purchased = OrderItem.objects.filter(
                order__user=user,
                order__status='PAID',
                product_variant__product=product
            ).exists()

            if not has_purchased:
                raise serializers.ValidationError(
                    "Solo puedes dejar reseñas en productos que hayas comprado."
                )

            # Verificar reseña duplicada
            if Review.objects.filter(product=product, user=user).exists():
                raise serializers.ValidationError(
                    "Ya dejaste una reseña para este producto."
                )

        return data


class ReviewStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de reseñas de un producto."""
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    distribution = serializers.DictField(child=serializers.IntegerField())


# =============================================================================
# Product Serializers
# =============================================================================

class ProductSerializer(serializers.ModelSerializer):
    """Serializer de lectura para productos con variantes y reseñas."""
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'base_price', 'image',
                  'is_active', 'category', 'variants', 'reviews',
                  'average_rating', 'total_reviews', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        result = obj.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else 0

    def get_total_reviews(self, obj):
        return obj.reviews.count()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listados de productos (sin reseñas completas)."""
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    variant_count = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'base_price', 'image',
                  'is_active', 'category_name', 'variant_count', 'min_price',
                  'average_rating', 'total_stock', 'created_at']

    def get_variant_count(self, obj):
        return obj.variants.filter(is_active=True).count()

    def get_min_price(self, obj):
        variants = obj.variants.filter(is_active=True)
        if variants.exists():
            prices = [v.price for v in variants]
            return min(prices) if prices else obj.base_price
        return obj.base_price

    def get_average_rating(self, obj):
        result = obj.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else 0

    def get_total_stock(self, obj):
        return sum(v.stock for v in obj.variants.filter(is_active=True))


class ProductWriteSerializer(serializers.ModelSerializer):
    """Serializer de escritura para crear/editar productos con variantes anidadas."""
    variants = ProductVariantWriteSerializer(many=True, required=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category',
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'base_price', 'image',
                  'is_active', 'category_id', 'variants']

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        product = Product.objects.create(**validated_data)

        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)

        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', None)

        # Actualizar campos del producto
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Si se envían variantes, actualizar/crear
        if variants_data is not None:
            existing_variant_ids = set(instance.variants.values_list('id', flat=True))
            incoming_variant_ids = set()

            for variant_data in variants_data:
                variant_id = variant_data.get('id')
                if variant_id and variant_id in existing_variant_ids:
                    # Actualizar variante existente
                    variant = ProductVariant.objects.get(id=variant_id, product=instance)
                    for attr, value in variant_data.items():
                        setattr(variant, attr, value)
                    variant.save()
                    incoming_variant_ids.add(variant_id)
                else:
                    # Crear nueva variante
                    ProductVariant.objects.create(product=instance, **variant_data)

        return instance


# =============================================================================
# Order Serializers
# =============================================================================


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
        read_only_fields = ['username']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})
        return attrs
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
