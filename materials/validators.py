import re

from rest_framework import serializers


def validate_video_url(value):
    """Валидатор: разрешает только ссылки на youtube.com."""
    if not value:
        return value

    match = re.search(r"(https?://[^\s]+)", value)
    if match:
        if not re.search(r"://.*youtube\.com", value):
            raise serializers.ValidationError("Разрешены только ссылки на youtube.com")
        return value
    else:
        return value
