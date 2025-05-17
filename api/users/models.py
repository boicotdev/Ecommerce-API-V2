from ast import mod
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.contrib.auth.models import Group, Permission
import uuid
from orders.models import Order
from shipments.models import Shipment


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Please provide an email address')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username=username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    dni = models.CharField(max_length=15, primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(
        default='users/avatar.jpg',
        upload_to='users/', blank=True, null=True)
    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    rol = models.CharField(max_length=15)
    # Evitar conflictos en groups y user_permissions
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions_set')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'dni']

    objects = CustomUserManager()

    def __str__(self) -> str:
        return f'{self.username}'




#TODO: DEPRECATED
class CustomerInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_addresses")
    full_name = models.CharField(max_length=55)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=10)
    special_notes = models.TextField(blank=True, null=True)

    # Una dirección puede estar asociada a múltiples órdenes o envíos
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_info')
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_info')

    def __str__(self):
        return f"{self.full_name} - {self.address} ({self.user.email})"




class Comment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "User comments+")
    raw_comment = models.TextField(max_length = 1000)
    pub_date = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"Comentario del usuario {self.user.username} | publicado {self.pub_date}"


#User profile settingss
class UserProfileSettings(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ownership')
    wants_receive_notifications = models.BooleanField(default=True)
    wants_receive_order_updates_notifications = models.BooleanField(default=True)
    wants_receive_order_updates_notifications = models.BooleanField(default=True)
    has_regard = models.BooleanField(default=False)
    shares = models.IntegerField(default=0)
    public_key = models.CharField(max_length=100, editable=False, default=str(uuid.uuid4)[15:])
    referrals_who_was_purchased = models.IntegerField(default=0)
    receive_monthly_newsletter = models.BooleanField(default=True)

