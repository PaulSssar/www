from django.db import models


class PaymentSettings(models.Model):
    """Модель настроек платежей"""
    shop_id = models.PositiveIntegerField(verbose_name='ID магазина')
    secret_key = models.CharField(max_length=100, verbose_name='Секретный ключ')
    is_active = models.BooleanField(default=False, verbose_name='Активность')

    def __str__(self):
        return f"Настройки платежей {self.shop_id}"

    class Meta:
        verbose_name = 'Настройки платежей'
        verbose_name_plural = 'Настройки платежей'


class Payment(models.Model):
    """Модель платежа"""
    STATUS_CHOICES = (
        ('pending', 'Ожидание'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Отменено'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    payment_url = models.URLField(blank=True, verbose_name='Ссылка на платеж')
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='payments', verbose_name='Заказ')

    def __str__(self):
        return f"Платеж {self.id} от {self.created_at}"

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

