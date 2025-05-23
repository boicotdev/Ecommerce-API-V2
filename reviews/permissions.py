from rest_framework.permissions import BasePermission


class IsOwnershipData(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsOwnerOfReview(BasePermission):
    """
    Permite el acceso solo si el usuario autenticado es dueño del objeto ProductReview.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
