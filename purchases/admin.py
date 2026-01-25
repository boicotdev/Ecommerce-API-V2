from django.contrib import admin

from .models import Purchase,PurchaseItem , MissingItems

admin.site.register([Purchase, PurchaseItem, MissingItems])
