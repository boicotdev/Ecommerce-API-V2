from rest_framework import serializers

from users.models import User
from .models import (
    Product,
    Category, UnitOfMeasure
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_unity(self, obj):
        return obj.measure_unity.unity if obj.measure_unity else None

    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category")
    unit = serializers.PrimaryKeyRelatedField(queryset=UnitOfMeasure.objects.all())
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'price', 'sku', 'description', 'stock', 'category_id',
                  'recommended', 'best_seller', 'discount_price', 'main_image', 'category', 'score', 'unit']

        def create(self, **validated_data):
            sku = validated_data.pop("sku", None)
            instance = self.Meta.model(**validated_data)
            if not sku:
                raise serializers.ValidationError({'sku': 'This field is required'})

            instance.sku = sku
            instance.save()
            return instance


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['dni', 'email', 'username', 'first_name', 'last_name', 'address', 'phone', 'avatar']


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'
