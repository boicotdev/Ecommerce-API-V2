import random
import string

from django.db import models

from products.models import Product, UnitOfMeasure


def generate_order_id(user_dni):
    suffix = str(user_dni)[-5:]
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"AVB{letters}{suffix}"


def generate_unique_order_id(user_dni):
    while True:
        custom_id = generate_order_id(user_dni)
        if not Order.objects.filter(id=custom_id).exists():
            return custom_id


class Order(models.Model):
    STATUS = (
        ("PENDING", "PENDING"),
        ("PROCESSING", "PROCESSING"),
        ("SHIPPED", "SHIPPED"),
        ("OUT_FOR_DELIVERY", "OUT_FOR_DELIVERY"),
        ("DELIVERED", "DELIVERED"),
        ("CANCELLED", "CANCELLED"),
        ("RETURNED", "RETURNED"),
        ("FAILED", "FAILED"),
        ("ON_HOLD", "ON_HOLD"),
    )

    DISCOUNT_TYPES = (
        ("REFERRAL", "Referral"),
        ("FIRST_PURCHASE", "First Purchase"),
        ("COUPON", "Coupon"),
        ("SEASONAL", "Seasonal Promo"),
        ("NONE", "No Discount"),
    )

    id = models.CharField(primary_key=True, max_length=20)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS, default="PENDING")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # no discounts
    discount_applied = models.BooleanField(default=False)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # total discount value
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPES,
        default="NONE"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # subtotal - discount + shipping

    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.id:
            user_dni = getattr(self.user, 'dni', "00000000")
            self.id = generate_unique_order_id(user_dni)

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Order {self.id} | {self.status} | {self.creation_date} | Last updated: {self.last_updated} | User: {self.user.username}"

    class Meta:
        ordering = ['-creation_date']

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()
    measure_unity = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL,
                                      verbose_name="unity")

    def __str__(self):
        return f"OrderProduct: {self.product.name} (x{self.quantity}) in Order {self.order.pk}"
