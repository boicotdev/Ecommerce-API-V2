from datetime import timedelta

from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from orders.models import Order
from shipments.models import DeliveryAddress
from .models import User, ReferralDiscount


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
        token['role'] = user.role
        token['is_superuser'] = user.is_superuser

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['dni'] = self.user.dni
        data['role'] = self.user.role
        data['is_superuser'] = self.user.is_superuser

        return data


class UserSerializer(serializers.ModelSerializer):
    dni = serializers.CharField()
    orders = serializers.SerializerMethodField()
    pending_orders_counter = serializers.SerializerMethodField()
    addresses_counter = serializers.SerializerMethodField()
    referrer_code = serializers.CharField(write_only=True, required=False)

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

    class Meta:
        model = User
        fields = ['dni', 'username', 'email', 'password',
                  'first_name', 'last_name', 'avatar', 'phone', 'address', 'role', 'date_joined',
                  'last_login', 'is_staff', 'is_superuser', 'orders', 'pending_orders_counter',
                  'addresses_counter', 'referred_by', 'referral_code', 'referrer_code']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        dni = validated_data.pop('dni', None)
        referrer_code = validated_data.pop('referrer_code', None)
        groups_data = validated_data.pop('groups', [])

        if not dni:
            raise serializers.ValidationError({"dni": "Este campo es obligatorio."})

        # Validar código de referido (si lo hay)
        referrer = None
        if referrer_code:
            try:
                referrer = User.objects.get(referral_code=referrer_code)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"referrer_code": f"El código de referido '{referrer_code}' no es válido."}
                )

        # Crear instancia del usuario (aún sin guardar)
        user = self.Meta.model(**validated_data)
        user.dni = dni
        if password:
            user.set_password(password)
        if referrer:
            user.referred_by = referrer

        user.save()

        # Asignar grupos (si aplica)
        for group in groups_data:
            user.groups.add(group)

        # Crear descuentos de referido si aplica
        expiry_date = timezone.now() + timedelta(days=30)

        if referrer:
            ReferralDiscount.objects.update_or_create(
                user=referrer,
                defaults={'has_discount': True, 'expires_at': expiry_date}
            )

            ReferralDiscount.objects.update_or_create(
                user=user,
                defaults={'has_discount': True, 'expires_at': expiry_date}
            )
        else:
            #If user isn't referred by someone
            ReferralDiscount.objects.update_or_create(
                user=user,
                defaults={'has_discount': True, 'expires_at': expiry_date}
            )
        return user


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
