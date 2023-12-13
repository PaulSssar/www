# Generated by Django 4.2.7 on 2023-11-30 13:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('ritual', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='orderresponse',
            name='executor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ritual.executor', verbose_name='Исполнитель'),
        ),
        migrations.AddField(
            model_name='orderresponse',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order', verbose_name='Заказ'),
        ),
        migrations.AddField(
            model_name='order',
            name='additional_services',
            field=models.ManyToManyField(blank=True, related_name='order_additional_services', to='ritual.service', verbose_name='Дополнительные услуги'),
        ),
        migrations.AddField(
            model_name='order',
            name='cemetery',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ritual.cemetery', verbose_name='Кладбище'),
        ),
        migrations.AddField(
            model_name='order',
            name='executor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_executor', to='ritual.executor', verbose_name='Исполнитель'),
        ),
        migrations.AddField(
            model_name='order',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ritual.service', verbose_name='Услуга'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='notification',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='additional_options',
            field=models.ManyToManyField(blank=True, related_name='additional_options', to='ritual.service', verbose_name='Дополнительные опции'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.cart', verbose_name='Корзина'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ritual.service', verbose_name='Услуга'),
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(through='order.CartItem', to='ritual.service', verbose_name='Услуги'),
        ),
        migrations.AddField(
            model_name='cart',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL, verbose_name='Владелец корзины'),
        ),
    ]
