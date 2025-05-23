from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from products.serializers import UserDetailsSerializer
from shipments.models import Shipment, DeliveryAddress
from users.models import User


class ShipmentSerializer(ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    customer_details = UserDetailsSerializer(source='customer', read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'order', 'shipment_address', 'shipment_date',
            'shipment_city', 'zip_code', 'status',
            'customer', 'customer_details'
        ]

    def validate_customer(self, value):
        """Validar que el campo 'customer' sea obligatorio"""
        if not value:
            raise serializers.ValidationError("El campo customer es obligatorio.")
        return value

    def validate_order(self, value):
        """Evitar que una orden tenga más de un envío"""
        if Shipment.objects.filter(order=value).exists():
            raise serializers.ValidationError("Ya existe un envío asociado a esta orden.")
        return value


class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = '__all__'
