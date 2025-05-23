from django.urls import path

from reviews.views import ProductReviewAPIView, ProductReviewResponseAPIView, RetrieveProductReviews, \
    RetrieveAllProductReviews

urlpatterns = [
    path('reviews/<int:pk>/', ProductReviewAPIView.as_view()),
    path('reviews/', ProductReviewAPIView.as_view()),
    path('reviews/answers/<int:pk>/', ProductReviewResponseAPIView.as_view()),
    path('reviews/answers/', ProductReviewResponseAPIView.as_view()),
    path('products/reviews/<str:pk>/', RetrieveProductReviews.as_view()),
    path('products/reviews/', RetrieveAllProductReviews.as_view())
]
