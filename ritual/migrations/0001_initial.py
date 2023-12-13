# Generated by Django 4.2.7 on 2023-11-30 13:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия')),
                ('patronymic_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Отчество')),
                ('phone', models.CharField(max_length=30, unique=True, verbose_name='Телефон')),
                ('email', models.CharField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('avatar', models.CharField(blank=True, max_length=255, null=True, verbose_name='Аватар')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('is_active', models.BooleanField(blank=True, default=True, verbose_name='Активный?')),
                ('is_confirmed', models.BooleanField(default=False, verbose_name='Подтвержден?')),
                ('in_consideration', models.BooleanField(default=False, verbose_name='На рассмотрении?')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Сотрудник?')),
                ('is_execute', models.BooleanField(default=False, verbose_name='Исполнитель?')),
                ('confirmation_code', models.CharField(blank=True, max_length=6, null=True, verbose_name='Код подтверждения')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='CheckList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название объекта')),
                ('state', models.CharField(choices=[('normal', 'В норме'), ('needs_work', 'Необходимы работы')], default='normal', max_length=20, verbose_name='Состояние объекта')),
            ],
            options={
                'verbose_name': 'Чек-лист',
                'verbose_name_plural': 'Чек-листы',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название города')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/', verbose_name='Изображение')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
            },
        ),
        migrations.CreateModel(
            name='Executor',
            fields=[
                ('useraccounts_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('tg_id', models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Telegram ID')),
                ('rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3, verbose_name='Рейтинг')),
            ],
            options={
                'verbose_name': 'Исполнитель',
                'verbose_name_plural': 'Исполнители',
            },
            bases=('ritual.useraccounts',),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название услуги')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание услуги')),
                ('price', models.IntegerField(default=0, verbose_name='Цена услуги')),
                ('services', models.TextField(max_length=255, verbose_name='Что входит в услугу')),
                ('additional_services', models.ManyToManyField(blank=True, to='ritual.service', verbose_name='Дополнительные услуги')),
                ('cities', models.ManyToManyField(related_name='cities', to='ritual.city', verbose_name='Города')),
                ('images', models.ManyToManyField(blank=True, related_name='services', to='ritual.image', verbose_name='Изображения')),
            ],
            options={
                'verbose_name': 'Услуга',
                'verbose_name_plural': 'Услуги',
            },
        ),
        migrations.CreateModel(
            name='ReviewExecuter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Содержание отзыва')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Автор отзыва')),
                ('executor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_reviews', to='ritual.executor', verbose_name='Исполнитель')),
            ],
            options={
                'verbose_name': 'Отзыв исполнителя',
                'verbose_name_plural': 'Отзывы исполнителей',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст отзыва')),
                ('rating', models.IntegerField(default=5, verbose_name='Рейтинг')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='ritual.service', verbose_name='Услуга')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(verbose_name='Оценка')),
                ('executor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review_rating', to='ritual.reviewexecuter', verbose_name='Отзыв исполнителя')),
            ],
            options={
                'verbose_name': 'Рейтинг',
                'verbose_name_plural': 'Рейтинги',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст вопроса')),
                ('answer', models.TextField(blank=True, null=True, verbose_name='Ответ')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='ritual.service', verbose_name='Услуга')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
        migrations.CreateModel(
            name='OrderChecklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('normal', 'В норме'), ('needs_work', 'Необходимы работы')], default='normal', max_length=20, verbose_name='Состояние объекта')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ritual.checklist', verbose_name='Объект')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checklists', to='order.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Чек-лист заказа',
                'verbose_name_plural': 'Чек-листы заказов',
            },
        ),
        migrations.AddField(
            model_name='image',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_images', to='ritual.service'),
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Сообщение чата',
                'verbose_name_plural': 'Сообщения чата',
            },
        ),
        migrations.CreateModel(
            name='Cemetery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес кладбища')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ritual.city', verbose_name='Город')),
            ],
            options={
                'verbose_name': 'Кладбище',
                'verbose_name_plural': 'Кладбища',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст ответа')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='ritual.question', verbose_name='Вопрос')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.AddField(
            model_name='useraccounts',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ritual.city', verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='useraccounts',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='useraccounts',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
