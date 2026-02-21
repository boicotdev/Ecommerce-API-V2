from django.urls import path
from .views import BlogAPIView

urlpatterns = [
    path("blogs/", BlogAPIView.as_view()),
    path("blogs/<int:pk>/", BlogAPIView.as_view()),
]
