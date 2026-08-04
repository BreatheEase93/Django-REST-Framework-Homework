from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Course

User = get_user_model()


@shared_task
def send_notification_task(course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return  # курс удалён — ничего не делаем
    users = User.objects.filter(subscriptions__course=course)
    for user in users:
        send_email_task.delay(user.email, course.title)


@shared_task
def send_email_task(user_email, course_title):
    """Отправляе письмо с пользовотелю об изминениях в курсе"""
    try:
        send_mail(
            subject="Изменения в курсе",
            message=f"Произошли изменения в курсе: {course_title}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
        )
    except Exception as e:
        print(f"Ошибка при отправке письма пользователю {user_email}: {e}")
