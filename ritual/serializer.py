# serializers.py
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import City, Image, Review, Question, Answer, UserAccounts, ReviewExecuter, Rating, ChatMessage, \
    CheckList, OrderChecklist, SimpleService

User = get_user_model()


class CitySerializer(serializers.ModelSerializer):
    """Сериализатор города"""
    class Meta:
        model = City
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'image', 'image_url']

    def get_image_url(self, obj):
        # Предполагаем, что у вас есть метод для получения URL изображения
        return obj.image.url if obj.image else None



class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва"""
    class Meta:
        model = Review
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор вопроса"""
    class Meta:
        model = Question
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    """Сериализатор ответа"""
    class Meta:
        model = Answer
        fields = '__all__'


class BaseServiceSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)
    service_images = ImageSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    questions = QuestionSerializer(many=True)

    class Meta:
        model = SimpleService
        fields = ['name', 'description', 'price', 'cities', 'service_images', 'reviews', 'questions']


# Дополнительный сериализатор для вложенных услуг
class AdditionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleService
        fields = ['id', 'name', 'price']  # Укажите здесь поля, которые вы хотите отображать для вложенных услуг


# Сериализатор услуги, использующий базовый сериализатор и добавляющий дополнительные услуги
class ServiceSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)
    service_images = ImageSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    questions = QuestionSerializer(many=True)
    additional_services = AdditionalServiceSerializer(many=True, read_only=True)

    class Meta:
        model = SimpleService
        fields = ['name', 'description', 'price', 'cities', 'service_images', 'reviews', 'questions', 'additional_services']


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор авторизации пользователя"""
    phone = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        swagger_schema_fields = {
            "type": "object",
            "properties": {
                "phone": {
                    "type": "string",
                    "description": "Телефон пользователя"
                },
                "password": {
                    "type": "string",
                    "description": "Пароль пользователя"
                }
            }
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    phone = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('phone', 'email', 'first_name', 'password', 'is_execute')

    def create(self, validated_data):
        user = UserAccounts(
            phone=validated_data['phone'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            is_execute=validated_data.get('is_execute', False)
        )
        user.password = make_password(validated_data['password'])  # Хешируем пароль
        user.save()
        return user

    def validate_password(self, value):
        # Добавьте здесь свою логику проверки сложности пароля
        return value


class ReviewExecuterSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва исполнителя"""
    class Meta:
        model = ReviewExecuter
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    """Сериализатор рейтинга исполнителя"""
    class Meta:
        model = Rating
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    """Сериализатор сообщения чата"""
    class Meta:
        model = ChatMessage
        fields = ('id', 'text', 'created_at')


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccounts
        fields = ('id', 'first_name', 'last_name', 'patronymic_name', 'phone', 'email', 'avatar', 'date_joined', 'city', 'is_active', 'is_confirmed', 'in_consideration', 'is_staff', 'is_execute')



class CheckListSerializer(serializers.ModelSerializer):
    """Сериализатор чеклиста"""
    class Meta:
        model = CheckList
        fields = '__all__'

class OrderChecklistSerializer(serializers.ModelSerializer):
    """Сериализатор чеклиста заказа"""
    item = CheckListSerializer()

    class Meta:
        model = OrderChecklist
        fields = '__all__'
