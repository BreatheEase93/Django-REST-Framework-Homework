from rest_framework import generics, viewsets

from materials.models import Course, Lesson
from materials.permissions import UserPermissionsAll
from materials.serializers import CourseSerializer, LessonSerializer


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
