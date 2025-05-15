from rest_framework.views import APIView, Response
from rest_framework import status, generics
from rest_framework_simplejwt.views import  TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import LimitOffsetPagination

from .permissions import IsOwnerOrSuperUserPermission
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, CommentSerializer, ChangePasswordSerializer
from .models import User, Comment



#login view
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshPairView(TokenRefreshView):
    ...

class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalidar el token de refresh (requiere que el blacklisting esté habilitado)
            return Response({"message": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Token no válido."}, status=status.HTTP_400_BAD_REQUEST)


#create a new User instance
class UserCreateView(APIView):
    """
    Create a new `User` instance without any special permissions
    Any user can use this view to create an account
    """
    def post(self, request):
        username = request.data.get("username", None)
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        email = request.data.get("email", None)

        
        #validate if required fields are fulfilled
        if not username or not first_name or not last_name or not email:
            return Response({"message": "Some fields are missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if User.objects.filter(email = email).exists():
                return Response({"message": f"User with email {email} already exists!"}, status = status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username = username).exists():
                return Response({"message": f"User with username {username} already exists!"}, status = status.HTTP_400_BAD_REQUEST)

            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

#retrieve user
class UserDetailsView(APIView):
    permission_classes = [IsOwnerOrSuperUserPermission]

    def get(self, request):
        user_id = request.query_params.get("user", None)
        if not user_id:
            return Response({"message": "User ID is required"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk = user_id)
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": f"User with ID {user_id} wasn't found"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return  Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#update a single user
class UserUpdateView(APIView):
    """
    Handle a `User` instance edition
    You must provide a username of the user you want edit
    """
    def put(self, request):
        user_id = request.data.get("dni", None)

        if not user_id:
            return Response({"message": "User ID field is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if User.objects.filter(dni=user_id).exists():
                user_instance = User.objects.get(dni = user_id)
                # Pasar el usuario existente al serializador para su actualización
                user_serializer = UserSerializer(user_instance, data=request.data, partial=True)

                if user_serializer.is_valid():
                    user_serializer.save()
                    return Response(user_serializer.data, status=status.HTTP_200_OK)

                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": "Internal server error!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClientUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request):
        try:
            queryset = User.objects.filter(rol="Cliente")
            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = UserSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#remove a single user
class UserDeleteView(APIView):
    """
    View created to handle `User` deletions
    -params: username.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    def delete(self, request):
        dni = request.data.get("dni", None)
        if not dni:
            return Response({"message": "Username field is required!"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(dni = dni)
            user.delete()
            return Response({"message": "User was deleted successfully"}, status = status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentCreateView(APIView):
    def post(self, request):
        comment = request.data.get("raw_comment", None)
        user = request.data.get("user", None)


        #check if required fields are fulfilled
        if not comment or not user:
            return Response({"message": "All fields are required"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk = user)
            serializer = CommentSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(user = user)
                return Response(serializer.data, status = status.HTTP_201_CREATED)

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"message": "Bad Request"}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentRetrieveListView(APIView):
    """
    Any user can access to this view
    :return: An array of `Comment` objects
    """
    def get(self, request):
        try:
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentUserRemoveView(APIView):
    def delete(self, request):
        
        user_id = request.data.get("user", None)
        comment_id = request.data.get("comment", None)

        if not user_id or not comment_id:
            return Response({"message": "All fields are required"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk = user_id)
            comment = Comment.objects.get(pk = comment_id, user = user)
            comment.delete()

            return Response({"message": "Comment was deleted successfully"}, status = status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"message": f"User with ID {user_id} doesn't found"}, status = status.HTTP_400_BAD_REQUEST)
        
        except Comment.DoesNotExist:
            return Response({"message": f"Comment with ID {comment_id} doesn't found"}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestimonialsUserRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.query_params.get("user")

        if not user_id:
            return Response({"message": f"User ID wasn't provided"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk = user_id)
            testimonials = Comment.objects.filter(user = user)
            serializer = CommentSerializer(testimonials, many= True)
            return Response(serializer.data, status = status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message": f"User with ID wasn't found"}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestimonialUserRemoveView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        user_id = request.data.get("user", None)
        testimonial_id = request.data.get("testimonial", None)

        if not user_id or not testimonial_id:
            return Response({"message": f"User ID and testimonial ID is required"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk = user_id)
            testimonial = Comment.objects.get(pk = testimonial_id, user = user)
            testimonial.delete()
            return Response({"message": "Testimonial was deleted"}, status = status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"message": f"User with ID {user_id} wasn't found"}, status = status.HTTP_400_BAD_REQUEST)

        except Comment.DoesNotExist:
            return Response({"message": f"Testimonial with ID {testimonial_id} wasn't found"}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update_password(request.user)
            return Response({"message": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)