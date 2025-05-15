from django.contrib import admin
from .models import Shipment, DeliveryAddress

admin.site.register([Shipment, DeliveryAddress])