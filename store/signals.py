from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order


@receiver(pre_save, sender=Order)
def restore_stock_on_cancellation(sender, instance, **kwargs):
    """
    Cuando una orden cambia su estado a 'CANCELLED', restaura el stock
    de todas las variantes asociadas a esa orden.

    Usa pre_save para comparar el estado anterior con el nuevo y evitar
    restauraciones duplicadas.
    """
    # Solo procesar si la orden ya existe en la BD (no es nueva)
    if not instance.pk:
        return

    try:
        previous_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    # Solo restaurar si el estado cambió a CANCELLED desde otro estado
    if previous_order.status != 'CANCELLED' and instance.status == 'CANCELLED':
        for item in instance.items.select_related('product_variant').all():
            variant = item.product_variant
            variant.stock += item.quantity
            variant.save(update_fields=['stock'])
