import re

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from order.serializers import ExecutorSerializer
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from ritual.serializers import ServiceSerializer, UserRegistrationSerializer, UserLoginSerializer, \
    ReviewExecuterSerializer, RatingSerializer, ChatMessageSerializer, UserAccountSerializer, OrderChecklistSerializer, \
    UserUpdateSerializer, ExecutorTGUpdateSerializer, SimpleServiceSerializer, PasswordChangeSerializer, \
    SendMessageSerializer
from settings.models import EmailSettings
import random
from .models import UserAccounts, ReviewExecuter, Rating, ChatMessage, OrderChecklist, Executor, SimpleService
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

account_activation_token = PasswordResetTokenGenerator()


def validate_email(email):
    """Проверяет, соответствует ли email формату электронной почты."""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None


class CustomBackend(ModelBackend):
    def authenticate(self, request, phone=None, email=None, password=None, **kwargs):
        try:
            if phone:
                # Поиск пользователя по телефону
                user = UserAccounts.objects.filter(phone=phone).first()
                user.check_password(password)
                print(f"phone {user=}")
                return user
            else:
                # Поиск пользователя по email
                user = UserAccounts.objects.filter(email=email).first()
                user.check_password(password)
                print(f"email {user=}")
                return user
        except UserAccounts.DoesNotExist:
            return None
        except AttributeError:
            return None


# class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     Показ всех услуг
#     """
#     queryset = Service.objects.all()
#     serializer_class = ServiceSerializer
#
#     @swagger_auto_schema(operation_description="Получение списка всех услуг")
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)
#
#     @swagger_auto_schema(operation_description="Получение детальной информации об услуге")
#     def retrieve(self, request, *args, **kwargs):
#         return super().retrieve(request, *args, **kwargs)


class RegistrationView(APIView):
    """
    Регистрация нового пользователя
    """

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone', 'email', 'password'],
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Телефон пользователя'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Электронная почта пользователя'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя'),
                'is_execute': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                             description='Является ли пользователь исполнителем'),
            },
        ),
        responses={
            201: openapi.Response(
                description='Пользователь успешно зарегистрирован',
                examples={
                    'application/json': {
                        'response': "Successfully registered a new user.",
                        'phone': 'user_phone',
                        'email': 'user_email',
                        'first_name': 'user_first_name',
                        'is_execute': 'user_is_execute',
                        'token': {
                            'refresh': '...',
                            'access': '...',
                        }
                    }
                }
            ),
            400: 'Ошибка в данных'
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Создание и отправка ссылки для подтверждения
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(reverse('activate', args=[uid, token]))

            send_mail(
                'Подтверждение регистрации',
                f'Пожалуйста, перейдите по ссылке для подтверждения вашей учетной записи: {activation_link}',
                'rosrituals@ya.ru',
                [user.email],
                fail_silently=False,
            )
            refresh = RefreshToken.for_user(user)
            data = {
                'response': "Successfully registered a new user.",
                'phone': user.phone,
                'email': user.email,
                'first_name': user.first_name,
                'is_execute': user.is_execute,
                'token': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """ post:
        Авторизация пользователя
        Параметры:
        - phone: Телефон пользователя
        - password: Пароль пользователя
        """

    @swagger_auto_schema(
        operation_description="Авторизация пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['login', 'password'],
            properties={
                'login': openapi.Schema(type=openapi.TYPE_STRING, description='Телефон или почта пользователя'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль пользователя'),
            },
        ),
        responses={
            200: openapi.Response(
                description='Успешная авторизация',
                examples={
                    'application/json': {
                        'token': {
                            'refresh': '...',
                            'access': '...',
                        }
                    }
                }
            ),
            400: 'Неверные учетные данные'
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            login = serializer.validated_data['login']
            password = serializer.validated_data['password']

            # Определяем, является ли входной логин телефоном или почтой
            if validate_email(login):
                # Если login - это email, аутентификация с использованием email
                user = authenticate(request, email=login, password=password)
                print(f"{user=}")
            else:
                # В противном случае предполагаем, что это телефон
                user = authenticate(request, phone=login, password=password)
                print(f"{user=}")

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'token': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewExecuterViewSet(APIView):
    """
    API endpoint that allows executor's reviews to be viewed.
    """

    @swagger_auto_schema(
        operation_summary="Получение всех отзывов для исполнителя",
        operation_description="Этот эндпоинт возвращает список всех отзывов, оставленных для конкретного исполнителя.",
        manual_parameters=[
            openapi.Parameter('executor_id', openapi.IN_PATH, description="ID исполнителя", type=openapi.TYPE_INTEGER)],
        responses={
            200: ReviewExecuterSerializer(many=True),
            404: 'Исполнитель с таким ID не найден'
        }
    )
    def get(self, request, executor_id, *args, **kwargs):
        reviews = ReviewExecuter.objects.filter(executor__id=executor_id)
        serializer = ReviewExecuterSerializer(reviews, many=True)
        if reviews:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Исполнитель с таким ID не найден'}, status=status.HTTP_404_NOT_FOUND)


class RatingViewSet(APIView):
    """
    API endpoint that allows executor's ratings to be viewed.
    """

    @swagger_auto_schema(
        operation_summary="Получение всех рейтингов для исполнителя",
        operation_description="Этот эндпоинт возвращает список всех рейтингов, выставленных конкретному исполнителю.",
        manual_parameters=[
            openapi.Parameter('executor_id', openapi.IN_PATH, description="ID исполнителя", type=openapi.TYPE_INTEGER)],
        responses={
            200: RatingSerializer(many=True),
            404: 'Исполнитель с таким ID не найден'
        }
    )
    def get(self, request, executor_id, *args, **kwargs):
        ratings = Rating.objects.filter(executor__id=executor_id)
        serializer = RatingSerializer(ratings, many=True)
        if ratings:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Исполнитель с таким ID не найден'}, status=status.HTTP_404_NOT_FOUND)


class ChatMessageView(APIView):
    """Чат"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получение всех сообщений для чата",
        operation_description="Этот эндпоинт возвращает список всех сообщений для чата.",
        responses={
            200: ChatMessageSerializer(many=True),
        }
    )
    def get(self, request):
        # Получение всех сообщений для чата
        messages = ChatMessage.objects.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Текст сообщения'),
                'file': openapi.Schema(type=openapi.TYPE_FILE, description='Файл сообщения'),
            },
        ),
    )
    def post(self, request):
        # Отправка нового сообщенияp
        print(request.data)
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(author=request.user)  # Установка автора сообщения из токена
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """Получение информации о пользователе по токену"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получение информации о пользователе по токену",
        operation_description="Этот эндпоинт возвращает информацию о пользователе по токену.",
        responses={
            200: UserAccountSerializer(),
        }
    )
    def get(self, request):
        # Пользователь уже аутентифицирован, его экземпляр находится в request.user
        user = request.user
        serializer = UserAccountSerializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Обновление информации о пользователе",
        operation_description="Этот эндпоинт позволяет обновлять информацию о пользователе.",
        request_body=UserUpdateSerializer,
        responses={
            200: UserAccountSerializer(),
            400: "Неверный запрос"
        }
    )
    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Смена пароля пользователя",
        operation_description="Этот эндпоинт позволяет пользователю сменить свой пароль.",
        request_body=PasswordChangeSerializer,
        responses={200: "Пароль успешно изменен", 400: "Неверный запрос"}
    )
    def post(self, request):
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            if not user.check_password(old_password):
                return Response({"old_password": "Неверный старый пароль"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"success": "Пароль успешно изменен"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderChecklistViewSet(APIView):
    """
    API endpoint that allows executor's ratings to be viewed.
    """

    @swagger_auto_schema(
        operation_summary="Получение всех чеклистов для заказа",
        operation_description="Этот эндпоинт возвращает список всех чеклистов, выставленных конкретному заказу.",
        manual_parameters=[
            openapi.Parameter('order_id', openapi.IN_PATH, description="ID заказа", type=openapi.TYPE_INTEGER)],
        responses={
            200: OrderChecklistSerializer(many=True),
            404: 'Заказ с таким ID не найден'
        }
    )
    def get(self, request, order_id, *args, **kwargs):
        checklists = OrderChecklist.objects.filter(order__id=order_id)
        serializer = OrderChecklistSerializer(checklists, many=True)
        if checklists:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Заказ с таким ID не найден'}, status=status.HTTP_404_NOT_FOUND)


class RequestPasswordResetEmailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    """Запрос на сброс пароля"""

    @swagger_auto_schema(
        operation_summary="Запрос на сброс пароля",
        operation_description="Этот эндпоинт отправляет на почту пользователя новый пароль.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Электронная почта пользователя'),
            },
        ),
        responses={
            200: 'Если аккаунт с такой почтой существует, на нее отправлен новый пароль',
        }
    )
    def post(self, request):
        try:
            email = request.data.get('email')
            user = UserAccounts.objects.filter(email=email).first()

            # Проверка существования пользователя
            if not user:
                return Response({'error': 'No user associated with this email'},
                                status=status.HTTP_404_NOT_FOUND)

            # Проверка соответствия email
            if email != user.email:
                return Response({'error': 'Email does not match'}, status=status.HTTP_400_BAD_REQUEST)

            # Проверка валидности email
            # try:
            #     validate_email(email)
            # except ValidationError:
            #     return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

            if user:
                email_settings = EmailSettings.objects.first()  # Получение настроек почты
                print(email_settings)
                new_password = get_random_string(length=8)
                print(new_password)

                user.set_password(new_password)  # Задаем новый пароль
                user.save()

                email_content = f'Your new password is: {new_password}\nPlease change it after logging in.'
                num_sent = send_mail(
                    'Password Reset',  # Тема письма
                    email_content,  # Тело письма
                    "rosrituals@ya.ru",  # От кого
                    ['nickolayvan@gmail.com', email],  # Кому (список получателей)
                    fail_silently=False,
                )
                if num_sent > 0:
                    print("Письмо успешно отправлено.")
                else:
                    print("Письмо не было отправлено.")
                print('Email sent successfully')

            return Response({'message': 'If an account with this email exists, '
                                        'a new password has been sent.'}, status=status.HTTP_200_OK)

        except BadHeaderError:
            print("Ошибка в заголовке письма.")
        except Exception as e:
            print(f"Произошла ошибка при отправке письма: {e}")
            return Response({'error': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExecutorListView(APIView):
    """Получение списка исполнителей"""

    @swagger_auto_schema(
        operation_summary="Получение списка исполнителей",
        operation_description="Этот эндпоинт возвращает список всех исполнителей.",
        responses={
            200: ExecutorSerializer(many=True),
        }
    )
    def get(self, request):
        executors = Executor.objects.all()
        serializer = ExecutorSerializer(executors, many=True)
        return Response(serializer.data)


class ExecutorTGUpdateView(APIView):
    """Обновление Telegram ID исполнителя"""

    @swagger_auto_schema(
        operation_summary="Обновление Telegram ID исполнителя",
        operation_description="Этот эндпоинт позволяет обновлять Telegram ID исполнителя.",
        request_body=ExecutorTGUpdateSerializer,
        responses={
            200: 'Telegram ID успешно обновлен.',
            400: "Неверный запрос",
            404: 'Исполнитель с таким кодом подтверждения не найден.'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ExecutorTGUpdateSerializer(data=request.data)
        if serializer.is_valid():
            confirmation_code = serializer.validated_data['confirmation_code']
            tg_id = serializer.validated_data['tg_id']

            try:
                executor = Executor.objects.get(confirmation_code=confirmation_code)
                executor.tg_id = tg_id
                executor.save()
                return Response({'message': 'Telegram ID успешно обновлен.'}, status=status.HTTP_200_OK)
            except Executor.DoesNotExist:
                return Response({'error': 'Исполнитель с таким кодом подтверждения не найден.'},
                                status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def activate(request, uidb64, token):
    """Активация учетной записи пользователя"""
    try:
        print(f"{uidb64=}")
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserAccounts.objects.get(pk=uid)
        print(f"{user=}")
    except (TypeError, ValueError, OverflowError, UserAccounts.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        print("Активация прошла успешно")
        user.is_confirmed = True
        user.save()
        # Перенаправление на страницу успешной активации или входа
        return redirect('login')
    else:
        # Перенаправление на страницу ошибки активации
        return redirect('login')


class SimpleServiceList(APIView):
    """
    Показ всех упрощенных услуг.
    """

    @swagger_auto_schema(
        operation_summary="Получение списка всех упрощенных услуг",
        operation_description="Этот эндпоинт возвращает список всех упрощенных услуг.",
        responses={
            200: SimpleServiceSerializer(many=True),
        }
    )
    def get(self, request):
        print(f"{request=}")
        services = SimpleService.objects.all()
        print(f"{services=}")
        for service in services:
            print(f"{service.images}")
        serializer = SimpleServiceSerializer(services, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SimpleServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SimpleServiceDetail(APIView):
    """
    Показ, обновление или удаление конкретной упрощенной услуги.
    """

    @swagger_auto_schema(
        operation_summary="Получение детальной информации об упрощенной услуге",
        operation_description="Этот эндпоинт возвращает детальную информацию об упрощенной услуге.",
        responses={
            200: SimpleServiceSerializer(),
            404: 'Упрощенная услуга с таким ID не найдена'
        }
    )
    def get_object(self, pk):
        try:
            print(f"{pk=}")
            return SimpleService.objects.get(pk=pk)
        except SimpleService.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        print(f"{pk=}")
        service = self.get_object(pk)
        serializer = SimpleServiceSerializer(service)
        return Response(serializer.data)


class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Отправка сообщения с файлами",
        operation_description="Этот эндпоинт позволяет отправлять текстовое сообщение с прикреплёнными файлами.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Текст сообщения'),
                'files': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_FILE,
                        description='Файлы для отправки в чат'
                    ),
                    description='Список файлов для отправки в чат'
                )
            },
            required=['text']
        ),
        responses={
            201: ChatMessageSerializer(),
            400: 'Неверные данные'
        }
    )
    def post(self, request):
        try:
            print(f"{request=}")
            print(f"{request.data=}")
            # Извлечение данных из запроса
            data = request.data

            # Создание сериализатора с данными запроса
            serializer = SendMessageSerializer(data=data, context={'request': request})

            # Проверка валидности данных
            if serializer.is_valid():
                # Сохранение объекта сообщения вместе с файлами
                message = serializer.save()
                print(f"{message=}")

                # Возврат сериализованных данных сообщения
                print(f"{serializer.data=}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # В случае невалидных данных возврат ошибки
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Произошла ошибка при отправке сообщения: {e}")
            return Response({'error': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientAdminChatAPIView(APIView):
    """Чат с администратором"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получение списка сообщений для чата с администратором",
        operation_description="Этот эндпоинт возвращает список сообщений для чата с администратором.",
        responses={
            200: ChatMessageSerializer(many=True),
        }
    )
    def get(self, request):
        admin_users = UserAccounts.objects.filter(is_staff=True).values_list('id', flat=True)
        client_user = self.request.user

        messages = ChatMessage.objects.filter(
            (Q(author=client_user) & Q(recipient__in=admin_users)) |
            (Q(author__in=admin_users) & Q(recipient=client_user))
        ).order_by('created_at')

        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class UnreadMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получение списка непрочитанных сообщений",
        operation_description="Этот эндпоинт возвращает список непрочитанных сообщений.",
        responses={
            200: ChatMessageSerializer(many=True),
        }
    )
    def get(self, request):
        unread_messages = ChatMessage.objects.filter(is_read=False, author=request.user)
        serializer = ChatMessageSerializer(unread_messages, many=True)
        return Response(serializer.data)


class MarkMessageAsReadAPIView(APIView):
    """Пометка сообщения как прочитанного"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Пометка сообщения как прочитанного",
        operation_description="Этот эндпоинт помечает сообщение как прочитанное.",
        responses={
            204: "Сообщение успешно помечено как прочитанное.",
            404: "Сообщение с таким ID не найдено."
        }
    )
    def patch(self, request, pk):
        message = ChatMessage.objects.get(pk=pk, author=request.user)
        message.is_read = True
        message.save()
        return Response(status=204)
