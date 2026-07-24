from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from materials.models import Course, Lesson, Subscription
from materials.paginators import MyPagination
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

    pagination_class = MyPagination


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
    pagination_class = MyPagination

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


# --- Эндпоинт для toggle подписки ---


class CourseToggleSubscriptionAPIView(generics.GenericAPIView):
    """
    Эндпоинт для подписки/отписки от курса.
    POST /courses/<id>/toggle/ — создаёт подписку, если её нет,
    или удаляет, если она есть.
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = kwargs.get("pk")
        subscription = Subscription.objects.filter(
            user=request.user, course_id=course_id
        ).first()

        if subscription:
            # Если подписка есть — удаляем
            subscription.delete()
            return Response(
                {"message": "Вы отписались от курса"}, status=status.HTTP_200_OK
            )

        # Если подписки нет — создаём
        Subscription.objects.create(user=request.user, course_id=course_id)
        return Response(
            {"message": "Вы подписались на курс"}, status=status.HTTP_201_CREATED
        )
