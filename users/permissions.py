from rest_framework import permissions


class UserPermissionsAll(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешить вход только авторизованным
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 1. Суперюзера пускаем всегда
        if request.user.is_superuser:
            return True

        # 2. Любой авторизованный может смотреть
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # 3. Редактировать (PUT/PATCH/DELETE) может только владелец
        return obj == request.user
