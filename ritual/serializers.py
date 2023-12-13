# serializers.py
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import City, Image, Review, Question, Answer, UserAccounts, ReviewExecuter, Rating, ChatMessage, \
    CheckList, OrderChecklist, Executor, SimpleService, ChatMessageFile

User = get_user_model()

from django.contrib.auth import get_user_model

UserModel = get_user_model()

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
    login = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ['login', 'password']


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
    class Meta:
        model = ChatMessage
        fields = '__all__'

    def create(self, validated_data):
        return ChatMessage.objects.create(**validated_data)


class UserAccountSerializer(serializers.ModelSerializer):
    """Сериализатор данных пользователя"""
    class Meta:
        model = UserAccounts
        fields = ('id', 'first_name', 'last_name', 'patronymic_name', 'phone', 'email', 'avatar', 'date_joined',
                  'city', 'is_active', 'is_confirmed', 'in_consideration', 'is_staff', 'is_execute')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор обновления данных пользователя"""
    phone = serializers.CharField(required=False)

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'patronymic_name', 'email', 'avatar', 'city', 'phone']
        extra_kwargs = {
            'email': {'required': False},
        }

    def validate_phone(self, value):
        if UserAccounts.objects.filter(phone=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Этот номер телефона уже используется другим пользователем.")
        return value


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


class ExecutorSerializer(serializers.ModelSerializer):
    """Сериализатор исполнителя"""
    city = CitySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Executor
        fields = ('id', 'first_name', 'last_name', 'avatar', 'rating', 'city', 'tg_id')

    def get_rating(self, obj):
        # Ваш код для вычисления среднего рейтинга исполнителя
        return obj.rating  # Или вызов метода для расчета рейтинга, если он у вас есть


class ExecutorTGUpdateSerializer(serializers.Serializer):
    """Сериализатор обновления tg_id исполнителя"""
    confirmation_code = serializers.CharField(max_length=6)
    tg_id = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)


class SimpleServiceSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, source='simple_service_images')
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = SimpleService
        fields = ['id', 'name', 'description', 'price', 'images', 'reviews',]


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class SendMessageSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),  # Дочерний элемент для обработки файлов
        required=False
    )

    class Meta:
        model = ChatMessage
        fields = ['text', 'files']

    def save(self, **kwargs):
        author = self.context['request'].user
        text = self.validated_data['text']
        files_data = self.validated_data.get('files', [])

        print(f"Author: {author}")
        print(f"Text: {text}")
        print(f"Files data: {files_data}")

        chat_message = ChatMessage.objects.create(author=author, text=text)
        print(f"ChatMessage created")
        for file_data in self.validated_data.get('files', []):
            try:
                print(f"File data: {file_data}")
                ChatMessageFile.objects.create(chat_message=chat_message, file=file_data)
                print(f"ChatMessageFile created")
            except Exception as e:
                print(f"Ошибка при создании ChatMessageFile: {e}")

        return chat_message


class ChatMessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageFile
        fields = ['file']