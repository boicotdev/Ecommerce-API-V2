from rest_framework import serializers

from reviews.models import ProductReview
from reviews.serializers import ProductReviewSerializer
from users.models import User
from .models import (
    Product,
    Category, UnitOfMeasure
)

class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category")
    measure_unity = serializers.PrimaryKeyRelatedField(queryset=UnitOfMeasure.objects.all())
    category = serializers.SerializerMethodField(read_only=True)
    unit_measure = serializers.SerializerMethodField(read_only=True)
    reviews = serializers.SerializerMethodField(read_only=True)

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_unit_measure(self, obj):
        return obj.measure_unity.unity if obj.measure_unity else None

    def get_reviews(self, obj):
        reviews = ProductReview.objects.filter(product=obj)
        return ProductReviewSerializer(reviews, many=True).data


    class Meta:
        model = Product
        fields = [
            'name', 'price', 'sku', 'description', 'stock',
            'category_id', 'recommended', 'best_seller', 'discount_price',
            'main_image', 'category', 'score', 'measure_unity', 'unit_measure', 'reviews'
        ]

    def create(self, validated_data):
        sku = validated_data.pop("sku", None)
        if not sku:
            raise serializers.ValidationError({'sku': 'This field is required'})
        instance = self.Meta.model(**validated_data)
        instance.sku = sku
        instance.save()
        return instance



class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['dni', 'email', 'username', 'first_name', 'last_name', 'address', 'phone', 'avatar']

