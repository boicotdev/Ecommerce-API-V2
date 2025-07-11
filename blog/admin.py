from django.contrib import admin
from .models import BlogPost, BlogReview, Tag

admin.site.register([BlogPost, BlogReview, Tag])
