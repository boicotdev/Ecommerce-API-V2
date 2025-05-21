from django.urls import path

from .views import PurchaseCreateUpdateView, PurchaseDeleteView, PurchaseListView, PurchaseDetailView, \
    RetrieveMissingItemsView

urlpatterns = [
    #------------------------------------ Purchases -----------------------------
    path('purchases/', PurchaseCreateUpdateView.as_view()), # handle purchase creation
    path('purchases/delete/', PurchaseDeleteView.as_view()), # handle purchase deletion
    path('purchases/list/', PurchaseListView.as_view(), name='purchase-list'),  # Retrieve all purchases
    path('purchases/details/<str:id>/', PurchaseDetailView.as_view(), name='purchase-detail'),
    path('purchases/missing-items/', RetrieveMissingItemsView.as_view()),

]