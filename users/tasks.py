from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def check_inactive_users():
    # 1. Вычисляем дату 30 дней назад
    cutoff_date = timezone.now() - timedelta(days=30)

    # 2. Находим всех активных пользователей, у которых last_login < cutoff_date
    # (или last_login вообще None)
    inactive_users = User.objects.filter(is_active=True, last_login__lt=cutoff_date)

    # 3. Блокируем их
    for user in inactive_users:
        user.is_active = False
        user.save()
