from rest_framework.permissions import BasePermission

class IsOwnerOrSuperUserPermission(BasePermission):
    """
    Only can access to this view a superuser or an authenticated user
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user