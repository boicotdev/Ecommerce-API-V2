from rest_framework import serializers
from orders.models import OrderProduct, Order
from payments.serializers import PaymentSerializer
from products.serializers import ProductSerializer, UserDetailsSerializer
from users.models import User


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Serializa el producto relacionado

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'price', 'quantity']  # No hay un campo 'products' en OrderProduct


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(source='orderproduct_set', many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    user_details = UserDetailsSerializer(source='user', read_only=True)
    payment = PaymentSerializer()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_details', 'payment', 'creation_date', 'last_updated', 'status',
                  'products', 'subtotal', 'total', 'discount_applied', 'discount_value', 'discount_type']
