from rest_framework import generics

from users.models import User
from users.serializers import UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Контроллер для регистрации/создания нового пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListAPIView(generics.ListAPIView):
    """Контроллер для просмотра списка всех пользователей"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Контроллер для просмотра профиля конкретного пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    """Контроллер для редактирования данных пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDestroyAPIView(generics.DestroyAPIView):
    """Контроллер для удаления пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
