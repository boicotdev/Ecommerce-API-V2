from django.urls import path

from orders.views import OrderCreateView, OrderUserList, OrderUserRemove, OrderUserCancelView, OrdersDashboardView, \
    OrderDashboardDetailsView, AdminOrderCreateView, OrderDashboardUpdateView, OrderProductCreateView

urlpatterns = [
    # ------------------------ orders endpoints --------------------------
    path('carts/orders/create/', OrderCreateView.as_view()),  # create a new user order
    path('carts/orders/list/', OrderUserList.as_view()),  # retrieve all orders of a user
    path('carts/orders/order/delete/', OrderUserRemove.as_view()),  # delete an order
    path('orders/order/cancel/', OrderUserCancelView.as_view()),  # cancel an order
    path('dashboard/orders/', OrdersDashboardView.as_view()),  # retrieve all user orders
    path('dashboard/order/details/', OrderDashboardDetailsView.as_view()),  # retrieve details of an order
    path('dashboard/order/create/', AdminOrderCreateView.as_view()),
    path('dashboard/order/update/', OrderDashboardUpdateView.as_view()),

    # ------------------------- product-orders endpoints -------------------
    path('carts/orders/product-orders/create/', OrderProductCreateView.as_view()),

]