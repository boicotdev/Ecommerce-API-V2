from django.db import models

from products.models import Product, UnitOfMeasure


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    creation_date = models.DateTimeField(verbose_name="Cart creation", auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Cart: {self.name} (ID: {self.id}, User: {self.user.username})"

class ProductCart(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    measure_unity = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="unity")


    def __str__(self):
        return f"ProductCart: {self.product.name} x{self.quantity} in {self.cart.name}"
