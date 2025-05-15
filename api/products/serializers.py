from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from users.models import User
from .models import (
    Product,
    Category,
    ProductReview, UnitOfMeasure
)

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_unity(self, obj):
        return obj.measure_unity.unity if obj.measure_unity else None

    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category")
    measure_unity = serializers.PrimaryKeyRelatedField(queryset=UnitOfMeasure.objects.all())
    category = serializers.SerializerMethodField()
    unity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'price', 'sku', 'description', 'stock', 'category_id',
                  'recommended', 'best_seller', 'has_discount', 'discount_price', 'main_image', 'first_image', 'second_image', 'category', 'rank', 'measure_unity', 'unity']

        def create(self, **validated_data):
            print('validated data',validated_data)
            sku = validated_data.pop("sku", None)
            instance = self.Meta.model(**validated_data)
            if not sku:
                raise serializers.ValidationError({'sku': 'This field is required'})

            instance.sku = sku
            instance.save()
            return instance


class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields ='__all__'


class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['dni', 'email', 'username', 'first_name', 'last_name', 'address', 'phone', 'avatar']


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'


