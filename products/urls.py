from django.urls import path
from .views import (
    ProductImportView,
    ProductListView,
    ProductDetailsView,
    RetrieveLatestProducts, AdminProductAPIView

)
from products.categories.views import AdminCategoriesAPIView

urlpatterns = [
    # list all categories
    path('products/categories/', AdminCategoriesAPIView.as_view()),

    path('products/categories/<int:pk>/', AdminCategoriesAPIView.as_view()),
    path('products/import/', ProductImportView.as_view()),
    path('products/list/', ProductListView.as_view()),  # retrieve all products
    path('products/latest/', RetrieveLatestProducts.as_view()),
    # retrieve a single products
    path('products/product/details/', ProductDetailsView.as_view()),
    path('dashboard/products/', AdminProductAPIView.as_view()),

    path('dashboard/products/<str:sku>/', AdminProductAPIView.as_view())
]
