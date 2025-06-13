from django.urls import path

from shipments.views import DeliveryAddressesAPIView, ShipmentUpdateView, ShipmentListView, ShipmentCreateView

urlpatterns = [
    # -------------------------- Shipments endpoints --------------------
    path('orders/shipments/create/', ShipmentCreateView.as_view()),  # create a new shipment
    path('orders/shipments/', ShipmentListView.as_view()),  # retrieve all shipments
    path('orders/shipments/update/', ShipmentUpdateView.as_view()),  # update a Shipment admin permissions are required
    path('shipments/addresses/', DeliveryAddressesAPIView.as_view()),
    # update a Shipment admin permissions are required
    path('shipments/addresses/<int:pk>/', DeliveryAddressesAPIView.as_view()),
]