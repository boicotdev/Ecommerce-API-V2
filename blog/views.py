from blog.models import BlogPost
from blog.serializers import BlogPostSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404


class BlogAPIView(APIView):
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            try:
                blog = BlogPost.objects.get(pk=pk)
                serializer = BlogPostSerializer(blog)
                return Response(serializer.data)
            except BlogPost.DoesNotExist:
                return Response(
                    {"message": f"Blog with ID {pk} not fount"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        posts = BlogPost.objects.all()
        serializer = BlogPostSerializer(posts, many=True)

        return Response(serializer.data)

    def put(self, request, pk):
        try:
            blog = BlogPost.objects.get(pk=pk)
            serializer = BlogPostSerializer(blog, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BlogPost.DoesNotExist:
            return Response(
                {"error": f"Blog with ID {pk} was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"error": "Internal error server"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        blog = get_object_or_404(BlogPost, pk=pk)
        blog.delete()
        return Response({"message": "Blog deleted"}, status=status.HTTP_204_NO_CONTENT)
