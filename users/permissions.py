from rest_framework.permissions import BasePermission


class IsOwnerOrSuperUserPermission(BasePermission):
    """
    Only can access to this view a superuser or an authenticated user
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user


class IsOwnerOfProfileSettings(BasePermission):
    """
    Permite el acceso solo si el usuario autenticado es dueño del objeto UserProfileSettings.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
