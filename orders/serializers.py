from rest_framework import serializers
from orders.models import OrderProduct, Order
from payments.serializers import PaymentSerializer
from products.serializers import ProductSerializer, UserDetailsSerializer
from shipments.serializers import ShipmentSerializer
from users.models import User
from users.serializers import AdminSerializer


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(source='orderproduct_set', many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    payment = PaymentSerializer()
    shipping_details = ShipmentSerializer(source='shipment', read_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_details', 'payment', 'creation_date', 'last_updated', 'status',
                  'products', 'subtotal', 'total', 'discount_applied', 'discount_value', 'discount_type', 'shipping_details', 'shipping_cost']

    def get_user_details(self, obj):
        user = obj.user
        return AdminSerializer(user).data