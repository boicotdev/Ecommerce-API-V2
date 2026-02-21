from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from products.models import Product
from utils.utils import update_product_score
from .models import ProductReview, ReviewResponse
from .serializers import ProductReviewSerializer, ProductReviewResponseSerializer
from reviews.permissions import IsOwnershipData, IsOwnerOfReview


class ProductReviewAPIView(APIView):
    permission_classes = [IsOwnershipData, IsOwnerOfReview]

    def get_object(self, pk):
        review = get_object_or_404(ProductReview, pk=pk)
        self.check_object_permissions(self.request, review)
        return review

    def get(self, request, pk=None):
        if pk:
            review = self.get_object(pk)
            return Response(
                ProductReviewSerializer(review).data, status=status.HTTP_200_OK
            )
        else:
            reviews = ProductReview.objects.filter(user=request.user)
            permitted_reviews = [
                r for r in reviews if self.check_object_permissions(request, r) or True
            ]
            serializer = ProductReviewSerializer(permitted_reviews, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            product = Product.objects.filter(sku=request.data.get("product")).first()
            serializer.save(user=request.user)
            update_product_score(
                product, request.data.get("rating")
            )  # update product score
            product.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
            return Response(
                {"detail": "Method PUT require pk."}, status=status.HTTP_400_BAD_REQUEST
            )
        review = self.get_object(pk)
        serializer = ProductReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # actualiza la instancia
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        review.delete()
        return Response(
            {"message": "Product review was deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class ProductReviewResponseAPIView(APIView):
    permission_classes = [IsOwnershipData, IsOwnerOfReview]

    def get_object(self, pk):
        review_response = get_object_or_404(ReviewResponse, pk=pk)
        self.check_object_permissions(self.request, review_response)
        return review_response

    def get(self, request, pk=None):
        try:
            response = self.get_object(pk)
            return Response(ProductReviewResponseSerializer(response).data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        product_review = get_object_or_404(
            ProductReview, id=request.data["product_review"]
        )
        serializer = ProductReviewResponseSerializer(
            data=request.data, context={"product_review": product_review}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        response = self.get_object(pk)
        serializer = ProductReviewResponseSerializer(
            response, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        response = self.get_object(pk)
        response.delete()
        return Response(
            {"message": "Response was deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class RetrieveProductReviews(APIView):
    def get(self, request, pk=None):
        if pk:
            reviews = ProductReview.objects.filter(product__sku=pk)

            if not reviews.exists():
                return Response(
                    {"detail": "No reviews found for this product."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = ProductReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            reviews = ProductReview.objects.filter(user=request.user)
            serializer = ProductReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveAllProductReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        reviews = ProductReview.objects.all()
        return Response(ProductReviewSerializer(reviews, many=True).data)
