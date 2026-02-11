from django.urls import path

from orders.views import (
    OrderCreateView,
    OrderUserList,
    OrderDashboardDetailsView,
    AdminOrderCreateView,
    OrderProductCreateView,
    CheckOrderStatusView,
    OrdersFileUploadAPIView
)

urlpatterns = [
    # ------------------------ orders endpoints --------------------------
    path('carts/orders/create/', OrderCreateView.as_view()),  # create a new user order
    path('carts/orders/list/', OrderUserList.as_view()),  # retrieve all orders of a user
    path('dashboard/orders/details/', OrderDashboardDetailsView.as_view()),  # retrieve details of an order
    path('dashboard/orders/create/', AdminOrderCreateView.as_view()),
    path('orders/check/', CheckOrderStatusView.as_view()),
    path('dashboard/orders/import/', OrdersFileUploadAPIView.as_view()),

    # ------------------------- product-orders endpoints -------------------
    path('carts/orders/product-orders/create/', OrderProductCreateView.as_view()),

]
