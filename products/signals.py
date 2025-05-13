from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import ApparelSize

@receiver([post_save, post_delete], sender=ApparelSize)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    total_quantity = product.apparel_sizes.aggregate(total=Sum('quantity'))['total'] or 0
    product.quantity = total_quantity
    product.save()