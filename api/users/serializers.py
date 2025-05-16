from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from orders.models import Order
from shipments.models import DeliveryAddress
from .models import User, Comment

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    We're using rest_framework_simplejwt to handle authentications
    We're using email field to user identificate
      - params: {"email": "user email", "password": "user password"}
      - returns: {"access": "an access token", "refresh": "a refresh access token"}
      
    """


    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['rol'] = user.rol
        token['is_superuser'] = user.is_superuser

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['dni'] = self.user.dni
        data['rol'] = self.user.rol
        data['is_superuser'] = self.user.is_superuser

        return data


class UserSerializer(serializers.ModelSerializer):
    dni = serializers.CharField()
    orders = serializers.SerializerMethodField()
    pending_orders_counter = serializers.SerializerMethodField()
    addresses_counter = serializers.SerializerMethodField()
    review_counter = serializers.SerializerMethodField()


    def get_orders(self, obj):
        user = obj
        count_orders = Order.objects.filter(user=user)
        return len(count_orders)

    def get_pending_orders_counter(self, obj):
        user = obj
        count_orders = Order.objects.filter(user=user, status='PENDING')
        return len(count_orders)

    def get_addresses_counter(self, obj):
        try:
            return DeliveryAddress.objects.filter(customer=obj).count()
        except Exception as e:
            return 0

    def get_review_counter(self, obj):
        try:
            return Comment.objects.filter(user=obj).count()
        except Exception as e:
            return 0

    class Meta:
        model = User
        fields = ["dni", 'username', 'email', 'password',
                  'first_name', 'last_name', 'avatar', 'phone', 'address', 'rol', 'date_joined',
                  'last_login', 'is_staff', 'is_superuser', 'orders', 'pending_orders_counter',
                  'addresses_counter', 'review_counter']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        dni = validated_data.pop('dni', None)
        if not dni:
            raise serializers.ValidationError({"dni": "This field is required"})
        # Extraer datos del campo groups
        groups_data = validated_data.pop('groups', [])

        instance = self.Meta.model(**validated_data)
        if dni:
            instance.dni = dni
        if password is not None:
            instance.set_password(password)
        instance.save()

        # Agregar los grupos después de guardar el usuario
        for group_data in groups_data:
            instance.groups.add(group_data)

        return instance


class CommentSerializer(serializers.ModelSerializer):
    def get_user_fullname(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name and obj.user.last_name else "Uknown"

    def get_user_avatar(self, obj):
        return obj.user.avatar.url if obj.user.avatar.url else "undefined"
    user_fullname = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()




    class Meta:
        model = Comment
        fields = ['id', 'raw_comment', 'pub_date', 'user_avatar', 'user_fullname']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError('Passwords don\'t match')
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password']:
            raise serializers.ValidationError({'confirm_password': 'Las contraseñas no coinciden'})
        return data

    def update_password(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user