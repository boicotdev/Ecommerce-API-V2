from django.urls import path

from .views import PurchaseCreateUpdateView, PurchaseDeleteView, PurchaseListView, PurchaseDetailView, \
    RetrieveMissingItemsView, PurchaseItemAPIView

urlpatterns = [
    #------------------------------------ Purchases -----------------------------
    path('dashboard/purchases/', PurchaseCreateUpdateView.as_view()), # handle purchase creation
    path('dashboard/purchases/items/', PurchaseItemAPIView.as_view()), # handle purchase creation
    path('dashboard/purchases/delete/', PurchaseDeleteView.as_view()), # handle purchase deletion
    path('dashboard/purchases/list/', PurchaseListView.as_view(), name='purchase-list'),  # Retrieve all purchases
    path('dashboard/purchases/details/<str:id>/', PurchaseDetailView.as_view(), name='purchase-detail'),
    path('dashboard/purchases/missing-items/', RetrieveMissingItemsView.as_view()),
]
