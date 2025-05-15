from django.urls import path
from .views import (
    ProductCreateView,
    ProductListView,
    ProductDetailsView,
    ProductUpdateView,
    ProductRemoveView,
    RetrieveLatestProducts

)
from products.categories.views import (
    CategoryCreateView,
    CategoryListView,
    CategoryUpdateView,
    CategoryRemoveView
)


urlpatterns = [
    path('products/categories/create/', CategoryCreateView.as_view()), #create a new category
    path('products/create/', ProductCreateView.as_view()), #create a new product
    path('products/categories/', CategoryListView.as_view()), #list all categories
    path('products/categories/update/', CategoryUpdateView.as_view()), #update a category
    path('products/categories/remove/', CategoryRemoveView.as_view()), #remove a category
    path('products/list/', ProductListView.as_view()), #retrieve all products
    path('products/latest/', RetrieveLatestProducts.as_view()),
    path('products/product/details/', ProductDetailsView.as_view()), #retrieve a single products
    path('products/product/update/', ProductUpdateView.as_view()),
    path('products/product/remove/', ProductRemoveView.as_view()), # remove a single product


]
