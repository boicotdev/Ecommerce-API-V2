from rest_framework.views import APIView, Response
from rest_framework import status
from products.serializers import CategorySerializer
from products.models import Category


#create a new category
class CategoryCreateView(APIView):
    def post(self, request):
        category_name = request.data.get("name", None)
        if not category_name:
            return Response({"message": "Category name is required"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            if Category.objects.filter(name = category_name).exists():
                return Response({"message": f"Category with name {category_name} already exists!"})
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#retrieve all categories from database
class CategoryListView(APIView):
    """
    Retrieve all categories from the database
    this view can access by any user
    """
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)


#edit a single category
class CategoryUpdateView(APIView):
    def put(self, request):
        category_id = request.data.get("id", None)
        if not category_id:
            return Response({"message": "Category id is required"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            if Category.objects.filter(pk = category_id).exists():
                category_instance = Category.objects.get(pk = category_id)
                serializer = CategorySerializer(category_instance, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status = status.HTTP_200_OK)
                return Response(serializer.errors, status = status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#remove a single categorie
class CategoryRemoveView(APIView):
    def post(self, request):
        category_id = request.data.get("id", None)
        if not category_id:
            return Response({"message": "Category name was required"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            category = Category.objects.get(pk = category_id)
            category.delete()
            return Response({"message": "Category was deleted"}, status = status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"message": f"Category with ID {category_id} doesn't exists."}, status = status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)



