from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import BasePermission


class AdminPermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsAdminOnly(BasePermission):
    """
    Permiso para permitir solo administradores.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class CanViewOrder(BasePermission):
    """
    Permite que un usuario vea solo sus órdenes,
    mientras que los administradores pueden ver todas.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated  # Solo usuarios autenticados

    def has_object_permission(self, request, view, obj):
        # Admins pueden ver cualquier orden
        if request.user.is_staff:
            return True
        # Usuarios normales solo pueden ver sus órdenes
        return obj.user == request.user
