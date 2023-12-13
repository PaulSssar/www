import uuid

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pay.serializers import PaymentSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment, PaymentSettings
import requests


class CreatePaymentView(APIView):
    """Создание платежа в ЮKassa"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Создание платежа",
        operation_description="Этот эндпоинт позволяет клиенту создать платеж в ЮKassa. "
                              "Необходимо предоставить сумму и идентификатор заказа.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_STRING, description='Сумма платежа'),
                'order': openapi.Schema(type=openapi.TYPE_INTEGER, description='Идентификатор заказа')
            },
            required=['amount', 'order'],
        ),
        responses={
            200: openapi.Response(
                description='Платеж успешно создан, и клиенту предоставлена ссылка на платеж.',
                examples={
                    'application/json': {
                        'url': 'https://url-to-yookassa-payment-page.com'
                    }
                }
            ),
            400: openapi.Response(
                description='Неверный запрос, данные не прошли валидацию.',
                examples={
                    'application/json': {
                        'amount': ['Это поле обязательно.'],
                        'order': ['Это поле обязательно.']
                    }
                }
            ),
            503: openapi.Response(
                description='Платежная система не настроена или временно недоступна.',
                examples={
                    'application/json': {
                        'error': 'Платежная система не настроена.'
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            # Проверяем, активны ли настройки платежей
            payment_settings = PaymentSettings.objects.first()
            if not payment_settings or not payment_settings.is_active:
                return Response({'error': 'Платежная система не настроена.'},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)

            payment = serializer.save()

            # Данные для создания платежа в ЮKassa, теперь с информацией о заказе
            payment_data = {
                "amount": {
                    "value": str(payment.amount),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": request.build_absolute_uri('/')  # Перенаправление на главную страницу
                },
                "capture": True,
                "description": f"Оплата заказа №{payment.order.id}"
            }

            # Уникальный ключ идемпотентности для предотвращения дублирования платежей
            idempotence_key = uuid.uuid4().hex

            # Отправляем запрос в ЮKassa для создания платежа
            headers = {
                'Idempotence-Key': idempotence_key,
                'Content-Type': 'application/json',
            }
            auth = (payment_settings.shop_id, payment_settings.secret_key)
            response = requests.post('https://api.yookassa.ru/v3/payments', json=payment_data, headers=headers,
                                     auth=auth)

            if response.status_code == 200:
                payment_url = response.json()['confirmation']['confirmation_url']
                return Response({'url': payment_url}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Не удалось создать платеж в ЮKassa'}, status=response.status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentWebhookView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """Обработка уведомления о платеже от ЮKassa"""

        payment_data = request.data
        payment_id = payment_data.get('object', {}).get('id')
        payment_status = payment_data.get('object', {}).get('status')

        if payment_status == 'succeeded':
            # Обновляем статус платежа в вашей базе данных
            try:
                payment = Payment.objects.get(id=payment_id)
                payment.status = 'paid'
                payment.save()
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status': 'OK'})


class PaymentStatusView(APIView):
    """Получение статуса платежа"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')
        try:
            payment = Payment.objects.get(order__id=order_id, order__user=request.user)
            return Response({'status': payment.status})
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)