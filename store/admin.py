from django.contrib import admin
from django.db.models import Sum, Count, Avg
from django.utils.html import format_html
from .models import Category, Product, ProductVariant, Coupon, Order, OrderItem, Review


# =============================================================================
# Personalización del Admin Site
# =============================================================================

admin.site.site_header = "KR Cases — Panel de Administración"
admin.site.site_title = "KR Cases Admin"
admin.site.index_title = "Gestión de la Tienda"


# =============================================================================
# Category Admin
# =============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug', 'product_count']
    search_fields = ['name']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Productos"


# =============================================================================
# Product Admin
# =============================================================================

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['model_name', 'color', 'material', 'sku', 'stock', 'price_override', 'is_active']
    readonly_fields = []


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'is_active',
                    'total_stock', 'variant_count', 'avg_rating', 'image_preview', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]
    list_editable = ['is_active']
    actions = ['activate_products', 'deactivate_products']

    def total_stock(self, obj):
        total = obj.variants.filter(is_active=True).aggregate(total=Sum('stock'))['total'] or 0
        if total == 0:
            return format_html('<span style="color: red; font-weight: bold;">0</span>')
        elif total <= 5:
            return format_html('<span style="color: orange; font-weight: bold;">{}</span>', total)
        return total
    total_stock.short_description = "Stock Total"

    def variant_count(self, obj):
        return obj.variants.filter(is_active=True).count()
    variant_count.short_description = "Variantes"

    def avg_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        if avg:
            return f"⭐ {avg:.1f}"
        return "—"
    avg_rating.short_description = "Rating"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 60px; object-fit: cover;" />',
                obj.image.url
            )
        return "—"
    image_preview.short_description = "Imagen"

    @admin.action(description="✅ Activar productos seleccionados")
    def activate_products(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} producto(s) activado(s).")

    @admin.action(description="❌ Desactivar productos seleccionados")
    def deactivate_products(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} producto(s) desactivado(s).")


# =============================================================================
# Coupon Admin
# =============================================================================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'active',
                    'valid_from', 'valid_to', 'usage_count']
    list_filter = ['active', 'discount_type', 'valid_from', 'valid_to']
    search_fields = ['code']
    list_editable = ['active']

    def usage_count(self, obj):
        return Order.objects.filter(coupon=obj, status='PAID').count()
    usage_count.short_description = "Usos"


# =============================================================================
# Order Admin
# =============================================================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_variant', 'quantity', 'price_at_purchase', 'item_total']
    # Permitimos editar product_variant y quantity si el admin necesita corregir un pedido manualmente,
    # aunque lo ideal es que las órdenes de e-commerce no se alteren mucho post-creación.

    def item_total(self, obj):
        return f"₲ {obj.price_at_purchase * obj.quantity:,.0f}"
    item_total.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'status_colored', 'formatted_total',
                    'items_count', 'tracking_number', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'tracking_number']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone', 'address')
        }),
        ('Estado de la Orden', {
            'fields': ('status', 'total_amount', 'tracking_number', 'notes')
        }),
        ('Pago', {
            'fields': ('coupon', 'payment_method'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_shipped', 'mark_as_cancelled']

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Cliente"

    def status_colored(self, obj):
        colors = {
            'PENDING': '#f39c12',
            'PAID': '#27ae60',
            'SHIPPED': '#3498db',
            'CANCELLED': '#e74c3c',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = "Estado"

    def formatted_total(self, obj):
        return f"₲ {obj.total_amount:,.0f}"
    formatted_total.short_description = "Total"

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Items"

    @admin.action(description="📦 Marcar como Enviado")
    def mark_as_shipped(self, request, queryset):
        count = queryset.filter(status='PAID').update(status='SHIPPED')
        self.message_user(request, f"{count} orden(es) marcada(s) como enviada(s).")

    @admin.action(description="🚫 Cancelar órdenes seleccionadas")
    def mark_as_cancelled(self, request, queryset):
        cancelled = 0
        for order in queryset.filter(status='PENDING'):
            order.status = 'CANCELLED'
            order.save()  # Trigger signal to restore stock
            cancelled += 1
        self.message_user(request, f"{cancelled} orden(es) cancelada(s). Stock restaurado.")


# =============================================================================
# Review Admin
# =============================================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating_stars', 'comment_short', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['product', 'user', 'rating', 'comment', 'created_at']

    def rating_stars(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return stars
    rating_stars.short_description = "Calificación"

    def comment_short(self, obj):
        return obj.comment[:80] + '...' if len(obj.comment) > 80 else obj.comment
    comment_short.short_description = "Comentario"
