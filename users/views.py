import requests
from django.conf import settings
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from materials.models import Course
from users.models import Payment, User
from users.permissions import UserPermissionsAll
from users.serializers import PaymentSerializer, UserSerializer
from users.services import create_checkout_session


class UserCreateAPIView(generics.CreateAPIView):
    """Контроллер для регистрации/создания нового пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserListAPIView(generics.ListAPIView):
    """Контроллер для просмотра списка всех пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Контроллер для просмотра профиля конкретного пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserUpdateAPIView(generics.UpdateAPIView):
    """Контроллер для редактирования данных пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermissionsAll]


class UserDestroyAPIView(generics.DestroyAPIView):
    """Контроллер для удаления пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class PaymentCreateAPIView(generics.CreateAPIView):
    """Контроллер для создания платежа с оплатой через Stripe"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создание платежа с оплатой через Stripe",
        request_body=PaymentSerializer,
        responses={
            201: PaymentSerializer,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
            502: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        if not course_id:
            return Response(
                {"error": "Не указан course"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        # Создаём Payment
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            payment_date=timezone.now().date(),
            sum_payment=course.price,
        )

        # Вызываем Stripe
        try:
            stripe_data = create_checkout_session(course)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        # Сохраняем ID в Payment
        payment.stripe_product_id = stripe_data["stripe_product_id"]
        payment.stripe_price_id = stripe_data["stripe_price_id"]
        payment.stripe_session_id = stripe_data["stripe_session_id"]
        payment.payment_url = stripe_data["payment_url"]
        payment.save()

        # Возвращаем данные платежа
        return Response(
            {
                "payment_url": stripe_data["payment_url"],
                "payment": PaymentSerializer(payment).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    """Контроллер для получения статуса платежа через Stripe"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()

        # Если нет stripe_session_id, возвращаем сохранённые данные
        if not payment.stripe_session_id:
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_200_OK,
            )

        # Получаем статус из Stripe
        headers = {"Authorization": f"Bearer {settings.STRIPE_SECRET_KEY}"}
        session_url = (
            f"{settings.STRIPE_BASE_URL}/checkout/sessions/{payment.stripe_session_id}"
        )
        session_response = requests.get(session_url, headers=headers)

        if session_response.status_code == 200:
            session_data = session_response.json()
            # Обновляем статус в нашей модели
            payment.status = session_data.get("status", "unknown")
            payment.save()
            return Response(
                {
                    "payment": PaymentSerializer(payment).data,
                    "stripe_status": session_data.get("status"),
                    "payment_status": session_data.get("payment_status"),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Не удалось получить статус из Stripe"},
            status=status.HTTP_502_BAD_GATEWAY,
        )


class PaymentListAPIView(generics.ListAPIView):
    """Контроллер для просмотра списка всех платежей"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    search_fields = ["course__title", "lesson__title", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
