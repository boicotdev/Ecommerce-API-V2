from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from payments.models import Payment
from products.serializers import UserDetailsSerializer
from shipments.models import Shipment, DeliveryAddress
from users.models import User


class ShipmentSerializer(ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    customer_details = UserDetailsSerializer(source='customer', read_only=True)
    amount = serializers.SerializerMethodField()

    @staticmethod
    def get_amount(shipment):
        try:
            order = shipment.order  # Acceder directamente a la orden
            payment = Payment.objects.filter(order=order).first()  # Buscar el pago asociado

            if payment:
                return payment.payment_amount  # Devolver el monto pagado

            return 0  # Si no hay pago, devolver 0
        except Exception as e:
            print(f"Error en get_amount: {e}")  # Log del error
            return 0

    class Meta:
        model = Shipment
        fields = [
            'id', 'order', 'shipment_address', 'shipment_date',
            'shipment_city', 'shipment_date_post_code', 'status',
            'customer', 'customer_details', 'amount'
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
