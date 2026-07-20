from rest_framework import permissions


class UserPermissionsAll(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешить всё для супкрпользователя
        if request.user.is_superuser:
            return True
        # Разрешить только чтение и изменение только для модераторов
        if request.user.groups.filter(name="moderators").exists():
            return request.method in ("GET", "HEAD", "OPTIONS", "PUT", "PATCH")
        # Разрешить чтение и создание только для авторизованных пользователей
        if request.user.is_authenticated:
            return request.method in (
                "GET",
                "HEAD",
                "OPTIONS",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            )

        else:
            return False

    def has_object_permission(self, request, view, obj):
        # Суперпользователь может всё
        if request.user.is_superuser:
            return True

        # Модератор может всё (кроме удаления)
        if request.user.groups.filter(name="moderators").exists():
            return True  # Может редактировать любые объекты

        # Обычный пользователь — только свои объекты
        return obj.author == request.user
