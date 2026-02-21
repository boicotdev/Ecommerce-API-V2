from rest_framework import serializers
from products.models import Product
from products.serializers import ProductSerializer
from orders.serializers import OrderSerializer
from .models import PurchaseItem, Purchase, MissingItems


class PurchaseItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()
    estimated_profit = serializers.ReadOnlyField()
    sale_price_per_weight = serializers.ReadOnlyField()

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    purchase = serializers.PrimaryKeyRelatedField(queryset=Purchase.objects.all())

    class Meta:
        model = PurchaseItem
        fields = [
            "id",
            "product",
            "purchase",
            "quantity",
            "purchase_price",
            "sell_percentage",
            "unit_measure",
            "subtotal",
            "estimated_profit",
            "sale_price_per_weight",
        ]


# class PurchaseItemSerializer(serializers.ModelSerializer):
#     subtotal = serializers.ReadOnlyField()
#     estimated_profit = serializers.ReadOnlyField()
#     sale_price_per_weight = serializers.ReadOnlyField()
#     product = ProductSerializer()
#
#     class Meta:
#         model = PurchaseItem
#         fields = ["id", "product", "quantity", "purchase_price", "sell_percentage", "unit_measure", "subtotal", "estimated_profit", "sale_price_per_weight"]


class PurchaseSerializer(serializers.ModelSerializer):
    purchase_items = PurchaseItemSerializer(many=True, read_only=True)
    estimated_profit = serializers.ReadOnlyField()

    class Meta:
        model = Purchase
        fields = [
            "id",
            "purchased_by",
            "purchase_date",
            "last_updated",
            "total_amount",
            "global_sell_percentage",
            "estimated_profit",
            "purchase_items",
        ]

    def validate_global_sell_percentage(self, value):
        """Check that the global percent is equal or grather than 10%"""
        if value is None or value < 10:
            raise serializers.ValidationError("The global percent must be 10% at least")
        return value


class MissingItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    order = OrderSerializer()

    class Meta:
        model = MissingItems
        fields = ["id", "product", "last_updated", "stock", "missing_quantity", "order"]
