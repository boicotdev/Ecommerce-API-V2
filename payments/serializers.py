from rest_framework.serializers import ModelSerializer

from payments.models import Payment, Coupon


class PaymentSerializer(ModelSerializer):
    """
    Serialize a `Payment` object and handle all logic to create a payment register
    ----
    """

    class Meta:
        model = Payment
        fields = "__all__"
        depth = 1


class CouponSerializer(ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
