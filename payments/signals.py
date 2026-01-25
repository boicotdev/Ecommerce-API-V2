from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import OrderProduct, StockMovement
from payments.models import Payment



@receiver(post_save, sender=Payment)
def save_stock_movement(sender, instance,created, **kwargs):
    if created:
        order = instance.order
        order_products = OrderProduct.objects.filter(order=order)
        stock_movements = []

        for op in order_products:
            product = op.product
            stock_movements.append(
                StockMovement(
                    product=product,
                    movement_type='OUT',
                    quantity=op.quantity,
                    reason='SALE',
                    related_order=order
                )
            )

        StockMovement.objects.bulk_create(stock_movements)
