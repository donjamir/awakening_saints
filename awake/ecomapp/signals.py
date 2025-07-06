from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BookOrder, Product

@receiver(post_save, sender=BookOrder)
def reduce_product_stock_when_collected(sender, instance, created, **kwargs):
    # Only update stock if this is an update (not initial creation)
    if not created and instance.status == 'collected':
        # Use a hidden flag to avoid re-processing
        if hasattr(instance, '_stock_already_reduced') and instance._stock_already_reduced:
            return

        for item in instance.items.all():
            product = item.product
            product.qty_in_stock = max(product.qty_in_stock - item.quantity, 0)
            product.save()

        # Prevent double-processing in the same session
        instance._stock_already_reduced = True
