from django.urls import path

from carts.views import CartCreateView, CartItemCreateView, CartUserListView, CartUserDelete, CartExistView

urlpatterns = [

    # ------------------------ carts endpoints -----------------------------
    path('carts/create/', CartCreateView.as_view()),  # create carts
    path('carts/items/create/', CartItemCreateView.as_view()),  # cart item create view
    path('carts/', CartUserListView.as_view()),  # list all carts of some user
    path('carts/delete/', CartUserDelete.as_view()),  # remove a unique cart
    path('carts/check/', CartExistView.as_view()),  # remove a unique cart
]