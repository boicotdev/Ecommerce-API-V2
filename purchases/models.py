import random
import string

from django.db import models

from products.models import Product, UnitOfMeasure
from orders.models import Order


class Purchase(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    purchased_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_admin"
    )
    purchase_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    total_amount = models.FloatField(default=0)  # Total purchase amount
    global_sell_percentage = models.FloatField(default=10)  # Global sell percentage
    estimated_profit = models.FloatField(default=0)  # Estimated profit

    def save(self, *args, **kwargs):
        if not self.id:
            admin_dni = getattr(self.purchased_by, 'dni', "00000000")
            self.id = generate_unique_id(admin_dni, purchase="True")
        super().save(*args, **kwargs)

    def update_totals(self):
        """Recalculates the total purchase amount and the estimated profit."""
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
    purchase_price = models.FloatField()  # Purchase price per item
    sell_percentage = models.FloatField(null=True, blank=True)
    unit_measure = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL)

    def get_sell_percentage(self):
        """
        Gets the sell percentage:
        uses the item percentage if defined, otherwise uses the Purchase global percentage.
        """
        return self.sell_percentage if self.sell_percentage is not None else self.purchase.global_sell_percentage

    def subtotal(self):
        """Calculates the total purchase cost for this product."""
        return self.quantity * self.purchase_price

    def estimated_profit(self):
        """Calculates the estimated profit based on the sell percentage."""
        sell_percentage = self.get_sell_percentage()
        profit_per_unit = self.purchase_price * (sell_percentage / 100)
        return self.quantity * profit_per_unit

    def sale_price_per_weight(self):
        """
        Calculates the sale price based on:
        subtotal, unit measure weight, and purchased quantity.
        """
        if not self.unit_measure or self.unit_measure.weight == 0:
            return 0  # Prevent division by zero or None errors

        sell_percentage = self.get_sell_percentage()

        # Apply the sell percentage to the subtotal
        subtotal_with_margin = self.subtotal() + (self.subtotal() * (sell_percentage / 100))

        # Calculate sale price based on unit measure weight and quantity
        return subtotal_with_margin / (self.unit_measure.weight * self.quantity)

    def __str__(self):
        if self.product:
            return (
                f"{self.quantity}x {self.product.name} "
                f"@ ${self.purchase_price} (Sell %: {self.get_sell_percentage()}%)"
            )
        return (
            f"{self.quantity}x Unknown "
            f"@ ${self.purchase_price} (Sell %: {self.get_sell_percentage()}%)"
        )


def generate_unique_id(user_dni, purchase=False):
    """
    Generates a unique ID with the following formats:
    - Order:   "AVBXX9YYYYYYYY" (XX = letters, 9 = number, YYYYYYYY = DNI)
    - Purchase: "COMP-AVBXX9YY" (XX = letters, 9 = number, YY = last 2 digits of DNI)
    """

    while True:
        if purchase:
            # Prefix for purchases: COMP-AVBXX9YY (last digits of DNI)
            prefix = (
                f"{random.choice(string.ascii_uppercase)}"
                f"{random.choice(string.ascii_uppercase)}"
                f"{random.randint(0, 9)}"
            )
            unique_id = f"COMP-AVB{prefix}{str(user_dni)[-4:]}"

            if not Purchase.objects.filter(id=unique_id).exists():
                return unique_id

        else:
            # Prefix for orders: AVBXX9YYYYYYYY
            prefix = (
                f"{random.choice(string.ascii_uppercase)}"
                f"{random.choice(string.ascii_uppercase)}"
                f"{random.randint(0, 9)}"
            )
            unique_id = f"AVB{prefix}{user_dni}"

            if not Order.objects.filter(id=unique_id).exists():
                return unique_id


class MissingItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="missing_item")
    last_updated = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField(default=1)
    missing_quantity = models.IntegerField(default=0)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name="pending_order"
    )

    def __str__(self):
        return (
            f"Item {self.product.sku} | "
            f"Order {self.order.id} | "
            f"Missing {self.missing_quantity}"
        )
