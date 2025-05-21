from rest_framework import status, generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .permissions import IsOwnerOrSuperUserPermission
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, ChangePasswordSerializer


# login view
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshPairView(TokenRefreshView):
    ...


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalidar el token de refresh (requiere que el blacklisting esté habilitado)
            return Response({'message': 'Sesión cerrada exitosamente.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Token no válido.'}, status=status.HTTP_400_BAD_REQUEST)


# create a new User instance
class UserCreateView(APIView):
    '''
    Create a new `User` instance without any special permissions
    Any user can use this view to create an account
    '''

    def post(self, request):
        required_fields = {'dni', 'username', 'email'}

        data = request.data
        missing_fields = required_fields - data.keys()

        if missing_fields:
            return Response(
                {'error': f'Missing required fields: {', '.join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # check if a User with the referral_code exists
        if request.data.get('referral_code'):
            try:
                User.objects.get(referral_code=request.data.get('referral_code'))
            except User.DoesNotExist:
                return Response({'error': 'User with referral_code not found!'}, status=status.HTTP_404_NOT_FOUND)

        # check if user with some required fields already exists.
        for field in required_fields:
            value = data.get(field)
            if value and User.objects.filter(**{field: value}).exists():
                return Response(
                    {'error': f'A user with {field} "{value}" already exists.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# retrieve user
class UserDetailsView(APIView):
    permission_classes = [IsOwnerOrSuperUserPermission]

    def get(self, request):
        user_id = request.query_params.get('user', None)
        if not user_id:
            return Response({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=user_id)
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': f'User with ID {user_id} was\'nt found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # update a single user
# class UserUpdateView(APIView):
#     """
#     API view to update a single User instance.
#     - You must provide the `dni` of the user to be updated in the payload.
#     - Accepts multipart/form-data for file uploads (e.g., avatar).
#     """
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#
#     def put(self, request):
#         dni = request.data.get('dni')
#
#         if not dni:
#             return Response(
#                 {"error": "Field 'dni' is required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Attempt to retrieve the user or return 404
#         user = get_object_or_404(User, dni=dni)
#
#         # Deserialize and validate the incoming data
#         serializer = UserSerializer(user, data=request.data, partial=True)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
class ClientUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            queryset = User.objects.filter(role='client')
            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = UserSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserUpdateView(APIView):
    '''
    Actualiza un usuario existente por su DNI.
    '''
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request):
        def flatten_data(data):
            return {key: value[0] if isinstance(value, list) else value for key, value in data.items()}

        raw_data = request.data
        print("📥 [DEBUG] request.data:")
        for k in raw_data:
            print(f"  - {k}: {raw_data.get(k)}")

        data = flatten_data(raw_data)

        dni = data.get('dni')
        if not dni:
            return Response({'message': 'Falta el campo dni'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_instance = User.objects.get(dni=dni)
            print(f"✅ [DEBUG] Usuario encontrado: {user_instance.username}")

            serializer = UserSerializer(user_instance, data=data, partial=True)
            if serializer.is_valid():
                updated_user = serializer.save()
                print("✅ [DEBUG] Usuario actualizado con éxito")
                return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)
            else:
                print("❌ [DEBUG] Errores de validación:")
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            print("❌ [DEBUG] Usuario no encontrado")
            return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"🔥 [ERROR] Excepción no controlada: {str(e)}")
            return Response({'message': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# remove a single user
class UserDeleteView(APIView):
    '''
    View created to handle `User` deletions
    -params: username.
    '''
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        dni = request.user.dni
        if not dni:
            return Response({'message': 'User DNI field is required!'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(dni=dni)
            user.delete()
            return Response({'message': 'User was deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update_password(request.user)
            return Response({'message': 'Contraseña actualizada correctamente.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
