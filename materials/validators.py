from urllib.parse import urlparse

from rest_framework import serializers


def validate_video_url(value):
    """Валидатор: разрешает только ссылки на youtube.com."""
    if not value:
        return value

    parsed = urlparse(value)
    hostname = parsed.hostname
    if hostname != "www.youtube.com" and hostname != "youtube.com":
        raise serializers.ValidationError("Разрешены только ссылки на youtube.com")
    else:
        return value
