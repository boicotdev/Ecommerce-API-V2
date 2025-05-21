import random
import string

from django.db import models

from products.models import Product, UnitOfMeasure
from orders.models import Order


# Create your models here.
class Purchase(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    purchased_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="user_admin")
    purchase_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    total_amount = models.FloatField(default=0)  # Total de compra
    global_sell_percentage = models.FloatField(default=10)  # Porcentaje de venta global
    estimated_profit = models.FloatField(default=0)  # Ganancia estimada

    def save(self, *args, **kwargs):
        if not self.id:
            admin_dni = getattr(self.purchased_by, 'dni', "00000000")
            self.id = generate_unique_id(admin_dni, purchase="True")
        super().save(*args, **kwargs)

    def update_totals(self):
        """Recalcula el total de la compra y la ganancia estimada."""
        total_cost = sum(item.subtotal() for item in self.purchase_items.all())
        self.total_amount = total_cost
        self.estimated_profit = sum(item.estimated_profit() for item in self.purchase_items.all())
        self.save()

    def __str__(self):
        return f"Purchase {self.id} | Total: ${self.total_amount} | Profit: ${self.estimated_profit}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="purchase_items")
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField()
    purchase_price = models.FloatField()  # Precio de compra unitario
    sell_percentage = models.FloatField(null=True, blank=True)
    unit_measure = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL)

    def get_sell_percentage(self):
        """Obtiene el porcentaje de venta: usa el del item si está definido, de lo contrario usa el de Purchase."""
        return self.sell_percentage if self.sell_percentage is not None else self.purchase.global_sell_percentage

    def subtotal(self):
        """Calcula el costo total de compra de este producto."""
        return self.quantity * self.purchase_price

    def estimated_profit(self):
        """Calcula la ganancia estimada en base al porcentaje de venta y el peso de la unidad de medida."""
        sell_percentage = self.get_sell_percentage()
        profit_per_unit = self.purchase_price * (sell_percentage / 100)
        return self.quantity * profit_per_unit

    def sale_price_per_weight(self):
        """Calcula el precio de venta basado en el subtotal, el peso de la unidad de medida y la cantidad comprada."""
        if not self.unit_measure or self.unit_measure.weight == 0:
            return 0  # Evita división por cero o errores con None

        sell_percentage = self.get_sell_percentage()

        # Aplicar el porcentaje de venta al subtotal
        subtotal_with_margin = self.subtotal() + (self.subtotal() * (sell_percentage / 100))

        # Calcular precio de venta basado en el peso de la unidad de medida y cantidad comprada
        return subtotal_with_margin / (self.unit_measure.weight * self.quantity)

    def __str__(self):
        if self.product:
            return f"{self.quantity}x {self.product.name} @ ${self.purchase_price} (Sell %: {self.get_sell_percentage()}%)"
        return f"{self.quantity}x Desconocido @ ${self.purchase_price} (Sell %: {self.get_sell_percentage()}%)"


def generate_unique_id(user_dni, purchase=False):
    """
    Genera un ID único con los siguientes formatos:
    - Orden: "ECCXX9YYYYYYYY" (XX = letras, 9 = número, YYYYYYYY = DNI)
    - Compra: "COMP-ECCXX9YY" (XX = letras, 9 = número, YY = últimos 2 dígitos del DNI)
    """

    while True:
        if purchase:
            # Prefijo para compras: COMP-ECCXX9YY (últimos 2 dígitos del DNI)
            prefix = f"{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.randint(0, 9)}"
            unique_id = f"COMP-ECC{prefix}{str(user_dni)[-4:]}"  # Últimos 2 dígitos del DNI

            if not Purchase.objects.filter(id=unique_id).exists():
                return unique_id

        else:
            # Prefijo para órdenes: ECCXX9YYYYYYYY
            prefix = f"{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.randint(0, 9)}"
            unique_id = f"ECC{prefix}{user_dni}"

            if not Order.objects.filter(id=unique_id).exists():
                return unique_id


class MissingItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="missing_item")
    last_updated = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField(default=1)
    missing_quantity = models.IntegerField(default=0)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name="pending_order")

    def __str__(self):
        return f"Item {self.product.sku} | Order {self.order.id} | Missing {self.missing_quantity}"
