from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer
from .models import ProductReview, ReviewResponse


class ProductReviewResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewResponse
        fields = '__all__'

    def create(self, validated_data):
        product_review = self.context.get('product_review')
        if not product_review:
            raise serializers.ValidationError("Product review is required.")

        response = ReviewResponse.objects.create(**validated_data)
        product_review.responses.add(response)
        return response

    def handle_product_rating_change(self, product, rating):
        product.score = rating
        product.save()


class ReviewResponseSerializer(serializers.ModelSerializer):
    publisher = serializers.SerializerMethodField()

    def get_publisher(self, obj):
        publisher: str = 'Unknown'
        if obj.user is not None:
            publisher = f'{obj.user.first_name} {obj.user.last_name}'
            return publisher
        return publisher

    class Meta:
        model = ReviewResponse
        fields = ['id', 'response', 'pub_date', 'publisher']


class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar']

class ProductReviewSerializer(serializers.ModelSerializer):
    responses = ReviewResponseSerializer(many=True, read_only=True)
    responses_ids = serializers.PrimaryKeyRelatedField(
        queryset=ReviewResponse.objects.all(),
        many=True,
        write_only=True,
        source='responses'
    )
    user = UserReviewSerializer(many=False, read_only=True)
    class Meta:
        model = ProductReview
        fields = ['id','user', 'product', 'comment', 'rating', 'rated_at', 'last_updated', 'responses','responses_ids', 'user']
