from django.contrib import admin
from payments.models import Payment, Coupon

admin.site.register([Payment, Coupon])

