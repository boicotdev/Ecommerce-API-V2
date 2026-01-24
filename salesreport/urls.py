
from django.urls import path
from .views import SalesReportAPIView


urlpatterns = [
    path('sales/reports/', SalesReportAPIView.as_view())
]
