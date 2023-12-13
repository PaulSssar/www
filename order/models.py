from django.apps import apps
from django.conf import settings

from django.db import models
from django.db.models import Sum
from ritual.models import UserAccounts


class Order(models.Model):
    STATUS_CHOICES = [
        ('searching', 'Поиск исполнителя'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнен'),
        ('pay_no', 'Не оплачен'),
    ]
    user = models.ForeignKey(UserAccounts, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='user_orders')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    birth_date = models.DateField(verbose_name='Дата рождения')
    death_date = models.DateField(verbose_name='Дата смерти')
    cemetery = models.ForeignKey('ritual.Cemetery', on_delete=models.SET_NULL, null=True, verbose_name='Кладбище')
    additional_message = models.TextField(blank=True, verbose_name='Дополнительное сообщение')
    executor = models.ForeignKey('ritual.Executor', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Исполнитель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    services = models.ManyToManyField('ritual.SimpleService', verbose_name='Услуги')
    total_cost = models.DecimalField(default=0.00, max_digits=10, decimal_places=2, verbose_name='Общая стоимость')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pay_no', verbose_name='Статус заказа')

    def calculate_total_cost(self):
        # Вычисление общей стоимости услуг
        return self.services.aggregate(Sum('price'))['price__sum'] or 0

    def save(self, *args, **kwargs):
        # Сначала сохраняем объект Order без учета услуг
        super().save(*args, **kwargs)

        # Теперь, когда у Order есть ID, можно добавить услуги
        if 'services' in kwargs:
            for service in kwargs['services']:
                self.services.add(service)

        # Пересчет общей стоимости с учетом услуг
        self.total_cost = self.calculate_total_cost()
        super().save(update_fields=['total_cost'])

    def __str__(self):
        return f"Заказ {self.id} от {self.full_name}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class CartItem(models.Model):
    """Модель элемента корзины"""
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE, verbose_name='Корзина')
    service = models.ForeignKey('ritual.SimpleService', on_delete=models.CASCADE, verbose_name='Услуга')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def get_cost(self):
        # Вычисляет стоимость услуги с учетом количества
        return self.service.price * self.quantity

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'


class Cart(models.Model):
    """Модель корзины"""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец корзины', related_name='cart')
    items = models.ManyToManyField('ritual.SimpleService', through='order.CartItem', verbose_name='Услуги')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def get_total_cost(self):
        # Получаем все CartItem объекты, связанные с этой корзиной
        cart_items = CartItem.objects.filter(cart=self)
        # Вычисляем общую стоимость, используя метод get_cost каждого CartItem
        return sum(item.get_cost() for item in cart_items)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Notification(models.Model):
    """Модель уведомления"""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    body = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.recipient.name} - {'Прочитано' if self.read else 'Не прочитано'}"

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class OrderResponse(models.Model):
    """Модель отклика на заказ"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    executor = models.ForeignKey("ritual.Executor", on_delete=models.CASCADE, verbose_name='Исполнитель')
    response_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата отклика')

    class Meta:
        verbose_name = 'Отклик на заказ'
        verbose_name_plural = 'Отклики на заказы'


class PhotoReport(models.Model):
    """Модель фотоотчета"""
    order = models.ForeignKey(Order, related_name='photo_reports', on_delete=models.CASCADE, verbose_name='Заказ')
    image = models.ImageField(upload_to='photo_reports/', verbose_name='Фотоотчет')

    def __str__(self):
        return f"Фотоотчет для заказа {self.order.id}"
