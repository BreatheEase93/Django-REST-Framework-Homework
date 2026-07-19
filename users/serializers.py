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

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            if request.user.is_superuser:
                return fields
            if request.user != self.instance:
                fields.pop("payment_history", None)
                fields.pop("password", None)
                fields.pop("last_name", None)

        return fields

    class Meta:
        model = User
        fields = "__all__"
