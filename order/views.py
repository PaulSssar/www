import uuid

import requests
from django.conf import settings
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from order.serializers import CartItemSerializer, CartSerializer, OrderSerializer, NotificationSerializer, \
    NotificationReadSerializer, ExecutorSerializer, AssignExecutorSerializer
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ritual.models import Executor, SimpleService

from .models import CartItem, Cart, Notification, OrderResponse, PhotoReport
from .models import Order


class OrderViewSet(viewsets.ModelViewSet):
    """API для заказов"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class CartListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получение списка корзин",
        operation_description="Этот эндпоинт возвращает список всех корзин текущего аутентифицированного пользователя. "
                              "Требуется передача токена аутентификации в заголовке запроса.",
        responses={200: CartSerializer(many=True)},
        security=[{'Bearer': []}]  # Указывает на необходимость использования токена
    )
    def get(self, request):
        carts = Cart.objects.filter(owner=request.user)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)


class CartCreateView(APIView):
    """API для создания корзины"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Создание или обновление корзины",
        operation_description="Этот эндпоинт позволяет создать новую корзину или добавить элементы в существующую корзину. "
                              "Требуется аутентификация пользователя.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='Список элементов для добавления в корзину',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'service': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID услуги'
                            ),
                            'quantity': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='Количество'
                            ),
                            'additional_options': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                description='Список ID дополнительных услуг (не обязательно)',
                                items=openapi.Schema(type=openapi.TYPE_INTEGER)
                            )
                        }
                    )
                )
            },
            required=['items']
        ),
        responses={
            201: CartSerializer(),
            400: 'Неверный запрос'
        }
    )
    def post(self, request):
        try:
            print(request.data)
            user = request.user
            print(user)
            # Проверяем, существует ли уже корзина у пользователя
            cart, created = Cart.objects.get_or_create(owner=user)
            print(f"{cart=}, {created=}")
            # Обрабатываем данные для элементов корзины
            serializer = CartItemSerializer(data=request.data.get('items', []), many=True)
            if serializer.is_valid():
                CartItem.objects.filter(cart=cart).delete()  # Очищаем текущие элементы в корзине
                for item_data in serializer.validated_data:
                    # Создаем CartItem без additional_options
                    item = CartItem.objects.create(cart=cart, service=item_data['service'],
                                                   quantity=item_data['quantity'])

                    # Добавляем additional_options, если они есть
                    if 'additional_options' in item_data:
                        for additional_option in item_data['additional_options']:
                            item.additional_options.add(additional_option)

                # Возвращаем обновленные данные корзины
                print(CartSerializer(cart).data)
                return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error': 'Ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderCreateFromCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Создание заказа из корзины",
        operation_description="API для создания заказа на основе данных из корзины.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='ФИО'
                ),
                'birth_date': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description='Дата рождения'
                ),
                'death_date': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description='Дата смерти'
                ),
                'cemetery_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID кладбища'
                ),
                'additional_message': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Дополнительное сообщение'
                )
            },
            required=['full_name', 'birth_date', 'death_date', 'cemetery_id']
        ),
        responses={
            201: OrderSerializer(),
            400: 'Неверный запрос'
        },
        security=[{'Bearer': []}]  # Указывает на необходимость использования токена
    )
    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(owner=user).first()

        if not cart:
            return Response({"error": "Корзина не найдена"}, status=400)

        # Дополнительные данные для заказа
        full_name = request.data.get('full_name')
        birth_date = request.data.get('birth_date')
        death_date = request.data.get('death_date')
        cemetery_id = request.data.get('cemetery_id')
        additional_message = request.data.get('additional_message', '')

        # Создание заказа без услуг
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            birth_date=birth_date,
            death_date=death_date,
            cemetery_id=cemetery_id,
            additional_message=additional_message,
            status='pay_no'
        )

        # Извлечение услуг из корзины и добавление их к заказу
        for item in CartItem.objects.filter(cart=cart):
            order.services.add(item.service)

        # Пересчет и сохранение общей стоимости
        order.total_cost = order.calculate_total_cost()
        order.save(update_fields=['total_cost'])

        print(OrderSerializer(order).data)
        return initiate_payment(order, request)

def initiate_payment(order, request):
    payment_data = {
        "amount": {
            "value": str(order.total_cost),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": request.build_absolute_uri('/')
        },
        "capture": True,
        "description": f"Оплата заказа №{order.id}"
    }

    # Отправка запроса в ЮKassa
    idempotence_key = uuid.uuid4().hex
    headers = {'Idempotence-Key': idempotence_key, 'Content-Type': 'application/json'}
    auth = (settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)
    response = requests.post('https://api.yookassa.ru/v3/payments', json=payment_data, headers=headers,
                             auth=auth)

    if response.status_code == 200:
        payment_url = response.json()['confirmation']['confirmation_url']
        return Response({'url': payment_url}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Ошибка создания платежа в ЮKassa'}, status=response.status_code)


class OrderListView(APIView):
    @swagger_auto_schema(
        operation_summary="Получение списка заказов по городу",
        operation_description="API для получения списка заказов, доступных в определенном городе для исполнителей.",
        manual_parameters=[openapi.Parameter('city', openapi.IN_QUERY, description="Город для поиска заказов", type=openapi.TYPE_STRING)],
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        city = request.query_params.get('city')
        print(city)
        orders = Order.objects.filter(cemetery__city=city)
        print(orders)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserOrderListView(APIView):
    @swagger_auto_schema(
        operation_summary="Получение списка заказов пользователя",
        operation_description="API для получения списка заказов, созданных конкретным пользователем.",
        manual_parameters=[openapi.Parameter('user_id', openapi.IN_QUERY, description="ID пользователя для поиска заказов", type=openapi.TYPE_INTEGER)],
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        orders = Order.objects.filter(user__id=user_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationListAPIView(APIView):
    """Получение списка уведомлений для текущего пользователя"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получение списка уведомлений для текущего пользователя",
        operation_description="API для получения списка уведомлений, адресованных текущему пользователю.",
        responses={200: NotificationSerializer(many=True)},
        security=[{'Bearer': []}]  # Указывает на необходимость использования токена
    )
    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user, read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationUpdateAPIView(APIView):
    """Пометка уведомления как прочитанного"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Пометка уведомления как прочитанного",
        operation_description="API для пометки уведомления как прочитанного.",
        responses={204: "Уведомление успешно помечено как прочитанное."},
        security=[{'Bearer': []}]  # Указывает на необходимость использования токена
    )
    def patch(self, request, pk):
        notification = Notification.objects.get(pk=pk, recipient=request.user)
        serializer = NotificationReadSerializer(notification, data={'read': True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderExecutorsListView(APIView):
    """Получение списка исполнителей для заказа"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получение списка исполнителей для заказа",
        operation_description="API для получения списка исполнителей, откликнувшихся на заказ.",
        responses={200: ExecutorSerializer(many=True)},
        security=[{'Bearer': []}]  # Указывает на необходимость использования токена
    )
    def get(self, request, order_id):
        print(order_id)
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            print(order)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден.'}, status=404)

        # Получаем список откликов исполнителей на заказ
        responses = OrderResponse.objects.filter(order=order)
        executors = [response.executor for response in responses]

        # Сериализуем информацию об исполнителях
        serializer = ExecutorSerializer(executors, many=True)
        return Response(serializer.data)


class AssignExecutorView(APIView):
    """Назначение исполнителя на заказ"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Назначение исполнителя на заказ",
        operation_description="API для назначения исполнителя на заказ.",
        request_body=AssignExecutorSerializer,
        responses={200: "Исполнитель успешно назначен."},
        security=[{'Bearer': []}]  # Указывает на необходимость использования токена
    )
    def post(self, request):
        serializer = AssignExecutorSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            executor_id = serializer.validated_data['executor_id']

            try:
                order = Order.objects.get(id=order_id)
                executor = Executor.objects.get(id=executor_id)
                order.executor = executor
                order.status = 'in_progress'  # Обновляем статус заказа
                order.save()
                return Response({'message': 'Исполнитель назначен.'}, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'error': 'Заказ не найден.'}, status=status.HTTP_404_NOT_FOUND)
            except Executor.DoesNotExist:
                return Response({'error': 'Исполнитель не найден.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoReportUploadView(APIView):
    """Загрузка фотоотчетов для заказа"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary="Загрузка фотоотчетов для заказа",
        operation_description="API для загрузки фотоотчетов для заказа.",
        manual_parameters=[
            openapi.Parameter('images', in_=openapi.IN_FORM, description="Фотоотчеты", type=openapi.TYPE_FILE,
                              required=True)
        ],
        responses={201: "Фотоотчеты успешно загружены."},
        security=[{'Bearer': []}],
        consumes=['multipart/form-data']  # Указывает, что API принимает многочастные формы
    )
    def post(self, request, order_id):
        order = Order.objects.filter(id=order_id, executor=request.user).first()
        if not order:
            return Response({'error': 'Заказ не найден или вы не являетесь исполнителем.'},
                            status=status.HTTP_404_NOT_FOUND)

        for file in request.FILES.getlist('images'):
            PhotoReport.objects.create(order=order, image=file)

        return Response({'message': 'Фотоотчеты успешно загружены.'}, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            print(self.request.user)
            return CartItem.objects.filter(cart__owner=self.request.user)

        else:
            # Возвращаем пустой QuerySet для неаутентифицированных пользователей
            return CartItem.objects.none()

    @swagger_auto_schema(
        operation_summary="Создание элемента корзины",
        operation_description="API для создания элемента корзины.",
        request_body=CartItemSerializer,
        responses={201: CartItemSerializer()},
        security=[{'Bearer': []}]
    )
    def perform_create(self, serializer):
        print(self.request.user)
        print(self.request)
        print(self.request.data)
        cart, _ = Cart.objects.get_or_create(owner=self.request.user)
        service_ids = serializer.validated_data.get('service_ids', [])

        for service_id in service_ids:
            service = SimpleService.objects.get(id=service_id)
            CartItem.objects.create(cart=cart, service=service, quantity=1)

        serializer = CartItemSerializer(cart.cartitem_set.all(), many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            print(self.request.user)
            return Cart.objects.filter(owner=self.request.user)
        else:
            # Возвращаем пустой QuerySet, если пользователь не аутентифицирован
            return Cart.objects.none()

    # @action(detail=False, methods=['get'])
    # def my_cart(self, request):
    #     cart, created = Cart.objects.get_or_create(owner=request.user)
    #     serializer = self.get_serializer(cart)
    #     return Response(serializer.data)