from rest_framework import permissions


class UserPermissionsAll(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешить всё для супкрпользователя
        if request.user.is_superuser:
            return True
        # Разрешить только чтение и изменение
        if request.user.groups.filter(name="moderators").exists():
            return request.method in ("GET", "PUT", "PATCH")
        else:
            return False
