from django.conf import settings
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name="Название курса")
    preview = models.ImageField(
        upload_to="courses/previews/",
        blank=True,
        null=True,
        verbose_name="Превью (картинка)",
    )
    description = models.TextField(blank=True, verbose_name="Описание курса")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    title = models.CharField(max_length=150, verbose_name="Название урока")
    description = models.TextField(blank=True, verbose_name="Описание урока")
    video_url = models.URLField(blank=True, verbose_name="Ссылка на видео")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["id"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"
