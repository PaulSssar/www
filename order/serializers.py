from django.db.models import Avg, Sum
from order.models import Order, Notification, PhotoReport
import logging
from rest_framework import serializers
from ritual.models import UserAccounts, Rating, Executor, SimpleService
from ritual.serializers import RatingSerializer, ReviewSerializer, CitySerializer, ServiceSerializer

from .models import CartItem, Cart
from ritual.serializers import SimpleServiceSerializer
logger = logging.getLogger(__name__)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.filter(owner=user).first()

        if not cart:
            raise serializers.ValidationError("Корзина не найдена.")

        # Создание заказа на основе данных из корзины и запроса
        order = Order.objects.create(
            user=user,
            full_name=validated_data.get('full_name'),
            birth_date=validated_data.get('birth_date'),
            death_date=validated_data.get('death_date'),
            cemetery=validated_data.get('cemetery'),
            additional_message=validated_data.get('additional_message', ''),
            # Установите основную услугу и дополнительные услуги, если они есть в запросе
            service=validated_data.get('service'),
            executor=None,  # или ваша логика для назначения исполнителя
            total_cost=cart.get_total_cost(),
            status='searching'  # или другой статус, если нужно
        )

        # Добавление дополнительных услуг из корзины в заказ
        for item in cart.items.all():
            order.additional_services.add(item.service)

        # Очистка корзины
        cart.items.clear()

        return order


class CartItemSerializer(serializers.ModelSerializer):
    service_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SimpleService.objects.all(),
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'service_ids', 'quantity']
        extra_kwargs = {'cart': {'read_only': True}}


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, source='cartitem_set', read_only=True)
    total_cost = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'owner', 'items', 'created_at', 'updated_at', 'total_cost', 'total_items']

    def get_total_cost(self, obj):
        return sum(item.service.price * item.quantity for item in obj.cartitem_set.all())

    def get_total_items(self, obj):
        return obj.cartitem_set.all().aggregate(count=Sum('quantity'))


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор уведомлений"""
    class Meta:
        model = Notification
        fields = ['id', 'title', 'body', 'read', 'timestamp']


class NotificationReadSerializer(serializers.ModelSerializer):
    """Сериализатор уведомлений"""
    class Meta:
        model = Notification
        fields = ['read']


class ExecutorSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(source='received_reviews', many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Executor
        fields = ('id', 'first_name', 'last_name', 'avatar', 'tg_id', 'city', 'ratings', 'reviews', 'average_rating',
                  "confirmation_code")

    def get_average_rating(self, obj):
        total_score = sum(rating.score for rating in obj.ratings.all())
        number_of_ratings = obj.ratings.count()
        return total_score / number_of_ratings if number_of_ratings > 0 else 0


class AssignExecutorSerializer(serializers.Serializer):
    """Сериализатор назначения исполнителя"""
    order_id = serializers.IntegerField()
    executor_id = serializers.IntegerField()


class PhotoReportSerializer(serializers.ModelSerializer):
    """Сериализатор фотоотчета"""
    class Meta:
        model = PhotoReport
        fields = ['image']

