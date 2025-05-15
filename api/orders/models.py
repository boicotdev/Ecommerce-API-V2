from django.db import models

from products.models import Product, UnitOfMeasure


# Create your models here.
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

    id = models.CharField(primary_key=True, max_length=20)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS, default="PENDING")


    def save(self, *args, **kwargs):
        if not self.id:  # Solo generar el ID si no existe
            user_dni = getattr(self.user, 'dni', "00000000")  # Obtener el DNI del usuario o usar por defecto
            self.id = 'scjcjcjcjs'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} | {self.status} | {self.creation_date} | Last updated: {self.last_updated} | User: {self.user.username}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()
    measure_unity = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL,
                                      verbose_name="unity")

    def __str__(self):
        return f"OrderProduct: {self.product.name} (x{self.quantity}) in Order {self.order.pk}"
