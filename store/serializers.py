from rest_framework import serializers
from django.db.models import Avg, Count, Q
from .models import Category, Product, ProductVariant, Coupon, Order, OrderItem, Review


# =============================================================================
# Category Serializers
# =============================================================================

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


# =============================================================================
# ProductVariant Serializers
# =============================================================================

class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer de lectura para variantes de producto."""
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
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user']

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
    """Serializer principal para crear órdenes (usado por checkout)."""
    items = OrderItemSerializer(many=True)
    coupon_code = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address',
                  'status', 'total_amount', 'payment_method', 'items', 'coupon_code']
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


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listado de órdenes."""
    items_count = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user_name', 'first_name', 'last_name', 'email',
                  'status', 'total_amount', 'payment_method', 'items_count',
                  'tracking_number', 'created_at', 'updated_at']

    def get_items_count(self, obj):
        return obj.items.count()

    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'Anónimo'


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para una orden individual con items expandidos."""
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()
    coupon_code = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'first_name', 'last_name', 'email',
                  'phone', 'address', 'notes', 'tracking_number',
                  'status', 'total_amount', 'coupon', 'coupon_code',
                  'payment_method', 'items', 'created_at', 'updated_at']
        read_only_fields = ['user', 'total_amount', 'coupon', 'payment_method',
                            'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'Anónimo'

    def get_coupon_code(self, obj):
        return obj.coupon.code if obj.coupon else None


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer para que el admin actualice el estado y tracking de una orden."""

    class Meta:
        model = Order
        fields = ['status', 'tracking_number', 'notes']

    def validate_status(self, value):
        valid_transitions = {
            'PENDING': ['PAID', 'CANCELLED'],
            'PAID': ['SHIPPED', 'CANCELLED'],
            'SHIPPED': [],
            'CANCELLED': [],
        }
        current_status = self.instance.status
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"No se puede cambiar de '{current_status}' a '{value}'. "
                f"Transiciones válidas: {valid_transitions.get(current_status, [])}"
            )
        return value
