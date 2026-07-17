from rest_framework import serializers

from users.models import Payment, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "city", "avatar")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "sum_payment",
            "payment_date",
            "payment_method",
            "course",
            "lesson",
        )
        read_only_fields = ("user",)
