from rest_framework.views import APIView, Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
from products.serializers import CategorySerializer
from products.models import Category


# Admin handle categories
class AdminCategoriesAPIView(APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request):
        category_name = request.data.get("name", None)
        if not category_name:
            return Response(
                {"message": "Category name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if Category.objects.filter(name=category_name).exists():
                return Response(
                    {"message": f"Category with name {category_name} already exists!"}
                )
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, pk=None):
        if pk:
            category = get_object_or_404(Category, pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            category = get_object_or_404(Category, pk=pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
