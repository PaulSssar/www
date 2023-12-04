# Generated by Django 4.2.7 on 2023-12-01 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ritual', '0004_alter_service_services'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_images', to='ritual.service'),
        ),
        migrations.CreateModel(
            name='SimpleService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название услуги')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание услуги')),
                ('price', models.IntegerField(default=0, verbose_name='Цена услуги')),
                ('images', models.ManyToManyField(blank=True, related_name='simple_services', to='ritual.image', verbose_name='Изображения')),
            ],
            options={
                'verbose_name': 'Упрощенная услуга',
                'verbose_name_plural': 'Упрощенные услуги',
            },
        ),
        migrations.AddField(
            model_name='image',
            name='simple_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='simple_service_images', to='ritual.simpleservice'),
        ),
    ]