# Generated by Django 4.2.7 on 2023-12-01 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ritual', '0005_alter_image_service_simpleservice_and_more'),
        ('order', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='additional_options',
        ),
        migrations.AlterField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(through='order.CartItem', to='ritual.simpleservice', verbose_name='Услуги'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ritual.simpleservice', verbose_name='Услуга'),
        ),
        migrations.AlterField(
            model_name='order',
            name='additional_services',
            field=models.ManyToManyField(blank=True, related_name='order_additional_services', to='ritual.simpleservice', verbose_name='Дополнительные услуги'),
        ),
        migrations.AlterField(
            model_name='order',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ritual.simpleservice', verbose_name='Услуга'),
        ),
    ]
