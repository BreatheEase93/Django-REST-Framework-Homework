from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from materials.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    """Тесты CRUD операций для уроков"""

    def setUp(self):
        """Создание тестовых данных"""
        self.client = APIClient()

        # Создаём пользователей
        self.superuser = User.objects.create_user(
            email="superuser@test.com",
            password="superpass123",
            is_superuser=True,
        )
        self.moderator = User.objects.create_user(
            email="moderator@test.com",
            password="modpass123",
        )
        self.moderator.groups.create(name="moderators")
        self.author = User.objects.create_user(
            email="author@test.com",
            password="authorpass123",
        )
        self.regular_user = User.objects.create_user(
            email="user@test.com",
            password="userpass123",
        )
        self.another_user = User.objects.create_user(
            email="another@test.com",
            password="anotherpass123",
        )

        # Создаём курс
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание курса",
            author=self.author,
        )

        # Создаём урок
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Тестовый урок",
            description="Описание урока",
            video_url="https://youtube.com/watch?v=test",
            author=self.author,
        )

        # URL для тестов
        self.lesson_create_url = "/lessons/create/"
        self.lesson_list_url = "/lessons/"
        self.lesson_detail_url = f"/lessons/{self.lesson.id}/"
        self.lesson_update_url = f"/lessons/update/{self.lesson.id}/"
        self.lesson_delete_url = f"/lessons/delete/{self.lesson.id}/"

    # ===================== ТЕСТЫ СОЗДАНИЯ УРОКА =====================

    def test_create_lesson_as_author(self):
        """Автор может создавать уроки"""
        self.client.force_authenticate(user=self.author)
        data = {
            "course": self.course.id,
            "title": "Новый урок",
            "description": "Описание нового урока",
            "video_url": "https://youtube.com/watch?v=new",
        }
        response = self.client.post(self.lesson_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.filter(title="Новый урок").count(), 1)

    def test_create_lesson_as_moderator(self):
        """Модератор не может создавать уроки (permissions.py запрещает POST)"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "course": self.course.id,
            "title": "Урок модератора",
            "description": "Описание урока модератора",
            "video_url": "https://youtube.com/watch?v=mod",
        }
        response = self.client.post(self.lesson_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_as_superuser(self):
        """Суперпользователь может создавать уроки"""
        self.client.force_authenticate(user=self.superuser)
        data = {
            "course": self.course.id,
            "title": "Урок суперпользователя",
            "description": "Описание урока",
            "video_url": "https://youtube.com/watch?v=super",
        }
        response = self.client.post(self.lesson_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_as_regular_user(self):
        """Обычный авторизованный пользователь может создавать уроки"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "course": self.course.id,
            "title": "Урок обычного пользователя",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=test",
        }
        response = self.client.post(self.lesson_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_with_invalid_url(self):
        """Создание урока с не-YouTube ссылкой должно отклониться"""
        self.client.force_authenticate(user=self.author)
        data = {
            "course": self.course.id,
            "title": "Урок с плохой ссылкой",
            "description": "Описание",
            "video_url": "https://stepik.org/course",
        }
        response = self.client.post(self.lesson_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ===================== ТЕСТЫ ПОЛУЧЕНИЯ УРОКОВ =====================

    def test_get_lesson_list_as_authenticated(self):
        """Авторизованный пользователь может получать список уроков"""
        self.client.force_authenticate(user=self.author)
        response = self.client.get(self.lesson_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_lesson_detail_as_author(self):
        """Автор может получать свой урок"""
        self.client.force_authenticate(user=self.author)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_lesson_detail_as_regular_user(self):
        """Обычный пользователь не может получить чужой урок (нет прав)"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_lesson_detail_as_anonymous(self):
        """Неавторизованный пользователь получает 401 (unauthorized)"""
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ===================== ТЕСТЫ ОБНОВЛЕНИЯ УРОКА =====================

    def test_update_lesson_as_author(self):
        """Автор может обновлять свой урок"""
        self.client.force_authenticate(user=self.author)
        data = {
            "title": "Обновлённый урок",
            "description": "Новое описание",
            "video_url": "https://youtube.com/watch?v=updated",
        }
        response = self.client.patch(self.lesson_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновлённый урок")

    def test_update_lesson_as_moderator(self):
        """Модератор может обновлять чужой урок"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "Обновлённый модератором",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=mod",
        }
        response = self.client.patch(self.lesson_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_as_another_user(self):
        """Другой пользователь не может обновлять чужой урок"""
        self.client.force_authenticate(user=self.another_user)
        data = {
            "title": "Чужое обновление",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=hack",
        }
        response = self.client.put(self.lesson_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ===================== ТЕСТЫ УДАЛЕНИЯ УРОКА =====================

    def test_delete_lesson_as_author(self):
        """Автор может удалять свой урок"""
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_as_moderator(self):
        """Модератор не может удалять уроки (permissions.py запрещает DELETE)"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_as_another_user(self):
        """Другой пользователь не может удалять чужой урок"""
        self.client.force_authenticate(user=self.another_user)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    """Тесты подписки на курс"""

    def setUp(self):
        """Создание тестовых данных"""
        self.client = APIClient()

        # Создаём пользователей
        self.user1 = User.objects.create_user(
            email="user1@test.com",
            password="pass123",
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com",
            password="pass123",
        )

        # Создаём курс
        self.course = Course.objects.create(
            title="Тестовый курс для подписки",
            description="Описание курса",
            author=self.user1,
        )

        # URL для подписки
        self.subscribe_url = f"/courses/{self.course.id}/subscribe/"
        self.unsubscribe_url = f"/courses/{self.course.id}/unsubscribe/"

    def test_subscribe_to_course(self):
        """Пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user1)
        data = {"course": self.course.id}
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Subscription.objects.filter(user=self.user1, course=self.course).exists()
        )

    def test_subscribe_as_different_user(self):
        """Другой пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user2)
        data = {"course": self.course.id}
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_subscription(self):
        """Попытка дублирования подписки должна отклониться"""
        self.client.force_authenticate(user=self.user1)
        # Первая подписка
        self.client.post(self.subscribe_url, {"course": self.course.id}, format="json")
        # Повторная подписка
        response = self.client.post(
            self.subscribe_url, {"course": self.course.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe_from_course(self):
        """Пользователь может отписаться от курса"""
        self.client.force_authenticate(user=self.user1)
        # Сначала подписываемся
        self.client.post(self.subscribe_url, {"course": self.course.id}, format="json")
        # Затем отписываемся
        response = self.client.delete(self.unsubscribe_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Subscription.objects.filter(user=self.user1, course=self.course).exists()
        )

    def test_unsubscribe_nonexistent(self):
        """Отписка от несуществующей подписки должна вернуть 404"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.unsubscribe_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_cannot_subscribe(self):
        """Неавторизованный пользователь не может подписаться"""
        data = {"course": self.course.id}
        response = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cannot_unsubscribe(self):
        """Неавторизованный пользователь не может отписаться"""
        response = self.client.delete(self.unsubscribe_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_delete_own_subscription(self):
        """Пользователь может удалить только свою подписку"""
        self.client.force_authenticate(user=self.user1)
        # Пользователь 1 подписывается
        self.client.post(self.subscribe_url, {"course": self.course.id}, format="json")
        # Пользователь 2 НЕ подписывается на этот курс
        self.client.force_authenticate(user=self.user2)
        # Пользователь 2 пытается удалить подписку пользователя 1
        response = self.client.delete(self.unsubscribe_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
