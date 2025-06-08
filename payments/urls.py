from django.urls import path

from payments.views import (CreatePaymentPreference, MercadoPagoPaymentView, PaymentDetailsViewView,
                            MercadoPagoWebhookView, CouponsAdminRetrieveView,
                            CouponCodeCheckView, CouponsCreateView, CouponUpdateView, CouponDeleteView,
                            )

urlpatterns = [
    # --------------------------------- Payments ---------------------------
    path('orders/carts/payments/', PaymentDetailsViewView.as_view()),
    # path('payments/report/<str:order_id>/', GenerateSalesReportAPIView.as_view()),
    path('payment/preferences/', CreatePaymentPreference.as_view()),
    path('process_payment/', MercadoPagoPaymentView.as_view()),
    path('webhook/mercadopago/', MercadoPagoWebhookView.as_view(), name='mercadopago-webhook'),

    # ---------------------------- Coupons endpoints -----------------------
    path('coupons/', CouponsAdminRetrieveView.as_view()),  # retrieve all coupons available on the shop
    path('coupons/validate/', CouponCodeCheckView.as_view()),  # check if a coupon is valid
    path('coupons/create/', CouponsCreateView.as_view()),  # create a new coupon
    path('coupons/update/', CouponUpdateView.as_view()),  # update a single coupon
    path('coupons/delete/', CouponDeleteView.as_view()),  # delete a single coupon
]
