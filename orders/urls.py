from django.urls import path

from orders.views import (
    OrderCreateView,
    OrderUserList,
    OrderDashboardDetailsView,
    AdminOrdersAPIView,
    OrderProductCreateView,
    CheckOrderStatusView,
    OrdersFileUploadAPIView,
)

urlpatterns = [
    # ------------------------ orders endpoints --------------------------
    path("carts/orders/create/", OrderCreateView.as_view()),  # create a new user order
    path("carts/orders/list/", OrderUserList.as_view()),  # retrieve all orders of a user
    path("dashboard/orders/details/", OrderDashboardDetailsView.as_view()),  # retrieve details of an order
    path("dashboard/orders/create/", AdminOrdersAPIView.as_view()),
    path("dashboard/orders/", AdminOrdersAPIView.as_view()), # we are getting all orders into the dashboard
    path("orders/check/", CheckOrderStatusView.as_view()),
    path("dashboard/orders/import/", OrdersFileUploadAPIView.as_view()),
    # ------------------------- product-orders endpoints -------------------
    path("carts/orders/product-orders/create/", OrderProductCreateView.as_view()),
]
