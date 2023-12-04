# Generated by Django 4.2.7 on 2023-12-02 20:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ritual', '0010_chatmessage_file'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0003_remove_cartitem_additional_options_alter_cart_items_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='additional_services',
        ),
        migrations.RemoveField(
            model_name='order',
            name='service',
        ),
        migrations.AddField(
            model_name='order',
            name='services',
            field=models.ManyToManyField(to='ritual.simpleservice', verbose_name='Услуги'),
        ),
        migrations.AlterField(
            model_name='order',
            name='executor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ritual.executor', verbose_name='Исполнитель'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('searching', 'Поиск исполнителя'), ('in_progress', 'В работе'), ('completed', 'Выполнен'), ('pay_no', 'Не оплачен')], default='pay_no', max_length=20, verbose_name='Статус заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
