from rest_framework import serializers

from users.models import Payment, User


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


class UserSerializer(serializers.ModelSerializer):
    payment_history = PaymentSerializer(many=True, read_only=True, source="payments")

    class Meta:
        model = User
        fields = ("id", "email", "phone", "city", "avatar", "payment_history")
