from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from materials.models import Course, Lesson


class CustomUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя, где логином является email."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Поле Email обязательно для заполнения")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по Email."""

    # Отключаем дефолтное поле username, так как логином будет email
    username = None

    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Номер телефона")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватарка"
    )

    # Меняем логику авторизации Django: теперь USERNAME_FIELD — это email
    USERNAME_FIELD = "email"
    # Поля, которые Django запросит при создании суперпользователя через терминал
    REQUIRED_FIELDS = []

    # Подключаем наш кастомный менеджер
    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return str(self.email)


class Payment(models.Model):
    "Класс для платежей"

    user = models.ForeignKey(
        User,
        related_name="payments",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    payment_date = models.DateField(verbose_name="Дата оплаты")
    course = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный курс",
    )
    lesson = models.ForeignKey(
        Lesson,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный урок",
    )
    sum_payment = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )
    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="cash",
        verbose_name="Способ оплаты",
    )

    stripe_product_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID продукта Stripe"
    )
    stripe_price_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID цены Stripe"
    )
    stripe_session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID сессии Stripe"
    )
    payment_url = models.URLField(
        blank=True, null=True, verbose_name="Ссылка на оплату"
    )
    status = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Статус платежа"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self) -> str:
        return f"{self.user} Дата: {self.payment_date}, cумма: {self.sum_payment}"
