from django.contrib import admin
from .models import (
    Product,
    Category,
    ProductReview,
    UnitOfMeasure
)

admin.site.register([Product, Category,ProductReview, UnitOfMeasure])