from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import EmailMessage, send_mail
from django.db import models
from django.db.models import ImageField
from filer.fields.image import FilerImageField
import random

from settings.models import EmailSettings
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    """Custom user model manager"""

    def create_user(self, phone, password=None, **extra_fields):
        print(f"{phone} {password} {extra_fields}")
        logger.info(f"Creating user with phone: {phone}")
        if not phone:
            raise ValueError('User must have a phone')

        # Генерация случайного пароля, если он не предоставлен
        if password is None:
            password = UserAccounts.objects.make_random_password()

        confirmation_code = str(random.randint(100000, 999999))

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)  # Хешируем пароль
        user.confirmation_code = confirmation_code
        user.save(using=self._db)

        # Вызываем отправку email после сохранения пользователя
        self.send_confirmation_code(user.email, user.confirmation_code, password)

        return user

    @staticmethod
    def send_confirmation_email(email, code):
        try:
            email_settings = EmailSettings.objects.first()
            subject = 'Ваш код подтверждения'
            message = f'Ваш код подтверждения: {code}'
            send_mail(
                subject,
                message,
                email_settings.email,
                [email],
                fail_silently=False,
            )

        except Exception as e:
            logger.error(f"Error sending email: {e}")

    def create_superuser(self, phone, password, is_superuser=True):
        if not phone:
            raise ValueError('User must have a phone')

        user = self.model(phone=phone, is_superuser=is_superuser, is_staff=True, is_active=True, is_confirmed=True)
        user.first_name = 'admin'
        user.last_name = 'admin'
        user.set_password(password)
        user.save()
        return user


class UserAccounts(AbstractBaseUser, PermissionsMixin):
    """Custom user model"""
    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фамилия')
    patronymic_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Отчество')
    phone = models.CharField(max_length=30, unique=True, verbose_name='Телефон')
    email = models.CharField(max_length=255, blank=True, null=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    city = models.ForeignKey('ritual.City', on_delete=models.SET_NULL, null=True, verbose_name='Город')

    objects = UserManager()

    is_active = models.BooleanField(blank=True, default=True, verbose_name='Активный?')
    is_confirmed = models.BooleanField(default=False, verbose_name='Подтвержден?')
    in_consideration = models.BooleanField(default=False, verbose_name='На рассмотрении?')
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник?')
    is_execute = models.BooleanField(default=False, verbose_name='Исполнитель?')

    confirmation_code = models.CharField(max_length=6, blank=True, null=True, verbose_name='Код подтверждения')

    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class City(models.Model):
    """Модель города"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название города')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


# class Service(models.Model):
#     """Модель услуги"""
#     name = models.CharField(max_length=255, verbose_name='Название услуги')
#     description = models.TextField(blank=True, null=True, verbose_name='Описание услуги')
#     price = models.IntegerField(default=0, verbose_name='Цена услуги')
#     cities = models.ManyToManyField('ritual.City', related_name='cities', verbose_name='Города')
#     additional_services = models.ManyToManyField('self', blank=True, verbose_name='Дополнительные услуги')
#     images = models.ManyToManyField('ritual.Image', related_name='services', blank=True, verbose_name='Изображения')
#     services = models.TextField(max_length=255, verbose_name='Что входит в услугу', blank=True, null=True)
#
#     def __str__(self):
#         return self.name
#
#     def some_method(self):
#         Order = apps.get_model('order', 'Order')
#
#     class Meta:
#         verbose_name = 'Услуга'
#         verbose_name_plural = 'Услуги'


class SimpleService(models.Model):
    """Упрощенная модель услуги"""
    name = models.CharField(max_length=255, verbose_name='Название услуги')
    description = models.TextField(blank=True, null=True, verbose_name='Описание услуги')
    price = models.IntegerField(default=0, verbose_name='Цена услуги')
    images = models.ManyToManyField('ritual.Image', related_name='simple_services', blank=True,
                                    verbose_name='Изображения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Упрощенная услуга'
        verbose_name_plural = 'Упрощенные услуги'


class Image(models.Model):
    # service = models.ForeignKey(Service, related_name='service_images', on_delete=models.CASCADE, null=True, blank=True)
    simple_service = models.ForeignKey(SimpleService, related_name='simple_service_images', on_delete=models.CASCADE,
                                       null=True, blank=True)
    image = FilerImageField(related_name='image_files', on_delete=models.CASCADE)

    # image = ImageField(upload_to='images/', blank=True, null=True, verbose_name='Изображение')

    def __str__(self):
        if self.simple_service:
            return f"Изображение для упрощенной услуги {self.simple_service.name}"
        else:
            return "Изображение без услуги"

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Review(models.Model):
    """Модель отзыва"""
    service = models.ForeignKey(SimpleService, on_delete=models.CASCADE, related_name='reviews', verbose_name='Услуга')
    user = models.ForeignKey('UserAccounts', on_delete=models.CASCADE, verbose_name="Пользователь")
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(default=5, verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.service.name}"

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Question(models.Model):
    """Модель вопроса"""
    service = models.ForeignKey(SimpleService, on_delete=models.CASCADE, related_name='questions',
                                verbose_name='Услуга')
    user = models.ForeignKey('UserAccounts', on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст вопроса')
    answer = models.TextField(blank=True, null=True, verbose_name='Ответ')

    def __str__(self):
        return f"Вопрос для {self.service.name} by {self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(models.Model):
    """Модель ответа"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    user = models.ForeignKey('UserAccounts', on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст ответа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f"Ответ от {self.user.first_name} {self.user.last_name} для вопроса {self.question.id}"

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class Cemetery(models.Model):
    """Модель кладбища"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    address = models.CharField(max_length=255, verbose_name='Адрес кладбища')

    def __str__(self):
        return f"{self.city.name}, {self.address}"

    class Meta:
        verbose_name = 'Кладбище'
        verbose_name_plural = 'Кладбища'


class CheckList(models.Model):
    STATE_CHOICES = [
        ('normal', 'В норме'),
        ('needs_work', 'Необходимы работы'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название объекта')
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='normal',
        verbose_name='Состояние объекта'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Чек-лист'
        verbose_name_plural = 'Чек-листы'


class OrderChecklist(models.Model):
    """Модель чек-листа заказа"""
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='checklists', verbose_name='Заказ')
    item = models.ForeignKey(CheckList, on_delete=models.CASCADE, verbose_name='Объект')
    state = models.CharField(
        max_length=20,
        choices=CheckList.STATE_CHOICES,
        default='normal',
        verbose_name='Состояние объекта'
    )

    class Meta:
        verbose_name = 'Чек-лист заказа'
        verbose_name_plural = 'Чек-листы заказов'


class Rating(models.Model):
    """Модель рейтинга исполнителя"""
    executor = models.ForeignKey(UserAccounts, related_name='ratings', on_delete=models.CASCADE,
                                 verbose_name='Исполнитель')
    score = models.PositiveIntegerField(verbose_name='Оценка')
    review = models.OneToOneField(
        "ReviewExecuter",
        on_delete=models.CASCADE,
        verbose_name='Отзыв исполнителя',
        related_name='review_rating'  # Исправлено с 'rating' на 'review_rating'
    )

    def __str__(self):
        return f"Рейтинг исполнителя {self.executor.first_name} {self.executor.last_name}"

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def update_executor_rating(self):
        total_score = sum(rating.score for rating in self.executor.ratings.all())
        number_of_ratings = self.executor.ratings.count()
        if number_of_ratings > 0:
            average_score = total_score / number_of_ratings
        else:
            average_score = 0
        self.executor.rating = average_score
        self.executor.save()


class ReviewExecuter(models.Model):
    """Модель отзыва исполнителя"""
    author = models.ForeignKey(UserAccounts, related_name='authored_reviews',
                               on_delete=models.CASCADE, verbose_name='Автор отзыва')
    executor = models.ForeignKey("Executor", related_name='received_reviews',
                                 on_delete=models.CASCADE, verbose_name='Исполнитель')
    content = models.TextField(verbose_name='Содержание отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return (f"Отзыв от {self.author.first_name} {self.author.last_name} для исполнителя {self.executor.first_name}"
                f" {self.executor.last_name}")

    class Meta:
        verbose_name = 'Отзыв исполнителя'
        verbose_name_plural = 'Отзывы исполнителей'


class Executor(UserAccounts):
    """Модель исполнителя"""
    tg_id = models.CharField(max_length=255, unique=True, verbose_name='Telegram ID', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name='Рейтинг')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Генерируем код подтверждения только при создании нового исполнителя
        if not self.pk:  # Проверяем, новый это объект или нет
            self.confirmation_code = str(random.randint(100000, 999999))
            UserManager.send_confirmation_email(self.email, self.confirmation_code)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'


class ChatMessage(models.Model):
    """Модель сообщения чата"""
    author = models.ForeignKey(UserAccounts, on_delete=models.CASCADE)
    recipient = models.ForeignKey(UserAccounts, on_delete=models.CASCADE, related_name='recipient', default=1)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True, verbose_name='Файл')

    def __str__(self):
        return f"Сообщение от {self.author.first_name} {self.author.last_name}"

    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'


class ChatMessageFile(models.Model):
    chat_message = models.ForeignKey(ChatMessage, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='chat_files/')

    def __str__(self):
        return f"Файл для {self.chat_message}"
