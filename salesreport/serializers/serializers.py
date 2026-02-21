from rest_framework import serializers


class SalesDataReportSerializer(serializers.Serializer):
    month = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = serializers.IntegerField()
    customers = serializers.IntegerField()


class TopProductsAnalyticsSerializer(serializers.Serializer):
    name = serializers.CharField()
    sales = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    growth = serializers.IntegerField()


class CustomerSegmentsAnalyticsSerializer(serializers.Serializer):
    CUSTOMER_SEGMENTS = (
        ("New Customer", "Nuevos Clientes"),
        ("Recurrent Customers", "Clientes Recurrentes"),
        ("VIP Customers", "Clientes VIP"),
    )

    COLORS = (
        ("#3B82F6", "#3B82F6"),
        ("#10B981", "#10B981"),
        ("#8B5CF6", "#8B5CF6"),
    )

    name = serializers.ChoiceField(CUSTOMER_SEGMENTS)
    value = serializers.IntegerField()
    percentage = serializers.IntegerField()
    color = serializers.ChoiceField(COLORS)


class RecentActivityAnalyticsSerializer(serializers.Serializer):
    ACTIONS = (
        ("New Order", "Nuevo Pédido"),
        ("New Customer", "Nuevo Cliente"),
        ("New Product Review", "Nueva reseña en el sitio web"),
        ("New Payment", "Pago registrado"),
    )
    action = serializers.ChoiceField(ACTIONS)
    customer = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    time = serializers.CharField()
