from django.contrib import admin
from .models import ProductReview, ReviewResponse

admin.site.register([ProductReview, ReviewResponse])
