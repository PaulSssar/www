from order.models import Order, Notification

from rest_framework import serializers
from .models import CartItem, Cart


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['service', 'additional_options', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['owner', 'items', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        cart = Cart.objects.create(owner=self.context['request'].user, **validated_data)
        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)
        return cart


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
