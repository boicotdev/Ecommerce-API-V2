from django.contrib import admin

from .models import Purchase, MissingItems

admin.site.register([Purchase, MissingItems])