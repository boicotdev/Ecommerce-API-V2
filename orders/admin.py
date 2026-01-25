from django.contrib import admin

from .models import Order, OrderProduct, StockMovement

admin.site.register([Order, OrderProduct, StockMovement])
