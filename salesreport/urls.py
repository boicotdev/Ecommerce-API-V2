
from django.urls import path
from .views import AnalyticsSalesReportsAPIView, ReportsAPIView


urlpatterns = [
    path('reports/', ReportsAPIView.as_view()),
    path('dashboard/analytics/', AnalyticsSalesReportsAPIView.as_view()),
]
