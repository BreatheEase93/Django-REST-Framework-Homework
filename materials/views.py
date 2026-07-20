from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from materials.models import Course, Lesson, Subscription
from materials.permissions import UserPermissionsAll
from materials.serializers import (
    CourseSerializer,
    LessonSerializer,
    SubscriptionSerializer,
)


# CRUD для Курсов с использованием Viewset
class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с моделью Курса (все CRUD операции)"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [UserPermissionsAll]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderators").exists():
            return Course.objects.all()
        return Course.objects.filter(author=user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# CRUD для Уроков с использованием Generic-классов
class LessonCreateAPIView(generics.CreateAPIView):
    """Контроллер для создания урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [UserPermissionsAll]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """Контроллер для получения списка уроков"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [UserPermissionsAll]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(author=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Контроллер для получения одного урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [UserPermissionsAll]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Контроллер для редактирования урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [UserPermissionsAll]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Контроллер для удаления урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [UserPermissionsAll]


# --- Эндпоинты для подписки ---


class CourseSubscribeAPIView(generics.CreateAPIView):
    """Эндпоинт для подписки на курс (POST /courses/<id>/subscribe/)"""

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Получаем ID курса из URL (например, /courses/1/subscribe/)
        course_id = self.kwargs.get("pk")
        # Привязываем текущего пользователя и курс
        serializer.save(user=self.request.user, course_id=course_id)


class CourseUnsubscribeAPIView(generics.DestroyAPIView):
    """Эндпоинт для отписки от курса (DELETE /courses/<id>/unsubscribe/)"""

    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        # Возвращаем только подписки текущего пользователя
        return Subscription.objects.filter(user=self.request.user)

    def get_object(self):
        # Ищем конкретную подписку на курс, который указан в URL
        course_id = self.kwargs["pk"]
        return get_object_or_404(self.get_queryset(), course_id=course_id)
