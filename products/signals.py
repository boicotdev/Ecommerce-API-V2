from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from .models import Product
from orders.models import Order, OrderProduct
from payments.models import Payment


@receiver(post_save, sender=Payment)
def update_order_and_stock(sender, instance, created, **kwargs):
    """
    Signal que actualiza el estado de la orden y ajusta el stock cuando se confirma un pago.
    Si un producto no tiene suficiente stock, solo se factura la cantidad disponible.
    """
    if created:
        try:
            order = instance.order
            order_products = OrderProduct.objects.filter(order=order)

            if order.status == "PENDING":
                order.status = "PROCESSING"
                order.save()

                # Procesar stock de cada producto en la orden
                for order_product in order_products:
                    product = order_product.product
                    if product.stock >= order_product.quantity:
                        # Stock suficiente: se descuenta la cantidad solicitada
                        product.stock = F("stock") - order_product.quantity
                        product.save()
                    elif product.stock > 0:
                        # Stock insuficiente: se factura solo lo disponible
                        print(
                            f"Stock insuficiente para {product.name}. Solo se facturan {product.stock} unidades."
                        )
                        order_product.quantity = (
                            product.stock
                        )  # Ajustar cantidad en la orden
                        order_product.save()
                        product.stock = 0  # Se vende todo lo disponible
                        product.save()
                    else:
                        # Sin stock: eliminar el producto de la orden
                        print(
                            f"Producto {product.name} sin stock. Eliminado de la orden."
                        )
                        order_product.delete()

        except Order.DoesNotExist:
            print("No se encontró la orden asociada al pago")
