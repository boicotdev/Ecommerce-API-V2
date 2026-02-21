from django.contrib import admin

from carts.models import ProductCart, Cart

# Register your models here.
admin.site.register([Cart, ProductCart])
