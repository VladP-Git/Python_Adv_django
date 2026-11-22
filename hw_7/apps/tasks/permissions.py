from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешает чтение всем авторизованным, а изменение и удаление — только владельцу."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
