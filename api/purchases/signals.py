from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from orders.models import Order, OrderProduct
from .models import Purchase, MissingItems


@receiver(post_save, sender=Purchase)
def calculate_missing_items(sender, instance, created, **kwargs):
    """
    Al crear una nueva compra (Purchase), recalcula los productos faltantes (MissingItems)
    en base a las órdenes en estado PENDING o PROCESSING.
    """
    try:
        if created:
            print("🔁 Calculando productos faltantes...")

            # Obtener todas las órdenes pendientes o en proceso
            pending_orders = Order.objects.filter(status__in=["PENDING", "PROCESSING"])
            print(f"📦 Órdenes activas encontradas: {pending_orders.count()}")

            for order in pending_orders:
                print(f"➡️ Procesando orden: {order.id}")

                order_products = OrderProduct.objects.filter(order=order)

                for op in order_products:
                    product = op.product
                    requested_qty = op.quantity
                    stock = product.stock  # suponiendo que tu modelo Product tiene este campo

                    print(f"🧮 Producto: {product.name} | Solicitado: {requested_qty} | Stock: {stock}")

                    # Calcular faltantes
                    missing_qty = max(0, requested_qty - stock)

                    # Actualizar o crear registro de MissingItem si hay déficit
                    if missing_qty > 0:
                        mi, created = MissingItems.objects.update_or_create(
                            product=product,
                            order=order,
                            defaults={
                                "missing_quantity": missing_qty,
                                "stock": stock
                            }
                        )
                        if created:
                            print(f"➕ MissingItem creado para '{product.name}' (orden {order.id})")
                        else:
                            print(f"♻️ MissingItem actualizado para '{product.name}' (orden {order.id})")

        print("✅ Cálculo de productos faltantes completado.")

    except Exception as e:
        print(f"❌ Error al calcular productos faltantes: {e}")
