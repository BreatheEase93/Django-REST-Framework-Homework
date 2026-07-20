from rest_framework import serializers

from materials.models import Course, Lesson, Subscription
from materials.validators import validate_video_url


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"

    def validate(self, data):
        text_fields = ["title", "description", "video_url"]

        for field_name in text_fields:
            if field_name in data and data[field_name]:
                validate_video_url(data[field_name])

        return data


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

    def validate(self, data):
        text_fields = ["title", "description"]

        for field_name in text_fields:
            if field_name in data and data[field_name]:
                validate_video_url(data[field_name])

        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "created_at"]
        read_only_fields = ["user", "created_at"]
