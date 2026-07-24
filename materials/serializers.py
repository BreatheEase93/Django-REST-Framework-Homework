from rest_framework import serializers

from materials.models import Course, Lesson, Subscription
from materials.validators import validate_video_url


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        validators=[validate_video_url], allow_blank=True, allow_null=True
    )

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        return obj.lessons.all().count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(course=obj, user=request.user).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "created_at"]
        read_only_fields = ["user", "created_at"]

    def validate(self, data):
        """Проверка на дублирование подписки"""
        user = self.context["request"].user
        course = data.get("course")
        if course and user.is_authenticated:
            if Subscription.objects.filter(user=user, course=course).exists():
                raise serializers.ValidationError("Вы уже подписаны на этот курс")
        return data
