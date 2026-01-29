from rest_framework import serializers


class  SalesDataReportSerializer(serializers.Serializer):
    month = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = serializers.IntegerField()
    customers = serializers.IntegerField()
