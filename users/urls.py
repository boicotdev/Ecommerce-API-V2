from django.urls import path

from .views import (
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
    UserDetailsView,
    CustomTokenObtainPairView,
    ClientUserListView, CustomTokenRefreshPairView,
    LogoutUserView, ChangePasswordView, NewsletterSubscriptionView, UserProfileSettingsAPIView, RetrieveAdminData
)

urlpatterns = [
    path("users/token/obtain/", CustomTokenObtainPairView.as_view()),  # token obtain
    path("users/token/refresh/", CustomTokenRefreshPairView.as_view()),  # token refresh
    path("users/data/", RetrieveAdminData.as_view()),  # retrieve admin data
    path("users/logout/", LogoutUserView.as_view()),  # kill a user session
    path("users/create/", UserCreateView.as_view()),  # create a new user
    path("dashboard/customers/", ClientUserListView.as_view()),  # retrieve all user clients
    path("users/user/", UserDetailsView.as_view()),  # retrieve all info of a single user
    path("users/update/", UserUpdateView.as_view()),  # edit a single user
    path("users/delete/", UserDeleteView.as_view()),  # delete a single user
    path('users/user/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path("newsletter/subscribe/", NewsletterSubscriptionView.as_view(), name="newsletter-subscribe"),
    path("users/profile/settings/", UserProfileSettingsAPIView.as_view()),
    path("users/profile/settings/update/", UserProfileSettingsAPIView.as_view()),
]
