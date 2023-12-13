from django.contrib import admin
from django.db.models import Sum
from .models import Order, CartItem, Cart, Notification, OrderResponse


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'birth_date', 'death_date', 'cemetery', 'executor', 'created_at', 'total_cost')
    list_filter = ('cemetery', 'executor', 'created_at')
    search_fields = ('full_name', 'user__phone', 'user__email')
    readonly_fields = ('created_at', 'total_cost')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'quantity', 'get_cost')
    search_fields = ('service__name', )
    list_filter = ('service',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'get_items', 'created_at', 'updated_at', 'get_total_cost')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('owner__phone', 'owner__email')
    readonly_fields = ('created_at', 'updated_at', 'get_total_cost')

    def get_items(self, obj):
        items = CartItem.objects.filter(cart=obj)  # Получаем элементы корзины для данной корзины
        return ", ".join([f"{item.service.name} (x{item.quantity})" for item in items])
    get_items.short_description = 'Элементы корзины'

    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = 'Общая стоимость'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'body', 'read', 'timestamp')
    list_filter = ('read', 'timestamp')
    search_fields = ('title', 'body')


@admin.register(OrderResponse)
class OrderResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'executor', 'response_date')
    list_filter = ('order', 'executor', 'response_date')
    search_fields = ('order__full_name', 'executor__first_name', 'executor__last_name')
