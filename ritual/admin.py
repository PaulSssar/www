from django.contrib.admin.widgets import AdminFileWidget, RelatedFieldWidgetWrapper

from django.db import models
from django.forms import Widget
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from ritual.forms import ServiceAdminForm
from ritual.models import City, Review, Question, Image, Answer, Cemetery, CheckList, Rating, \
    ReviewExecuter, Executor, SimpleService
from django.contrib import admin
from .models import UserAccounts


# from ritual.forms import ServiceForm

class CustomImageWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        html = ''
        if value:
            html = format_html('<img src="{}" height="100" />', value.url)
        return mark_safe(html) + super().render(name, value, attrs, renderer)


@admin.register(UserAccounts)
class UserAccountsAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'first_name', 'email', 'is_active', 'is_confirmed',
                    'in_consideration', 'is_staff', 'date_joined', 'send_message')
    search_fields = ('phone', 'first_name', 'last_name', 'patronymic_name', 'email')
    list_filter = ('is_active', 'is_confirmed', 'in_consideration', 'is_execute')
    readonly_fields = ('password', 'last_login', 'date_joined')  # date_joined оставлен только для чтения
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'patronymic_name', 'email', 'avatar')}),
        ('Permissions', {'fields': (
            'is_active', 'is_confirmed', 'in_consideration', 'is_staff', 'is_execute', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),  # убрать 'date_joined' отсюда
    )
    permissions_ = (
        (None, {'fields': ('phone', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'patronymic_name', 'email', 'avatar')}),
        ('Permissions', {'fields': (
            'is_active', 'is_confirmed', 'in_consideration', 'is_staff', 'is_superuser', 'groups',
            'user_permissions')}),
    )
    add_fieldsets = permissions_
    ordering = ('id', 'phone', 'first_name', 'email',)
    filter_horizontal = ('groups', 'user_permissions')

    def send_reply(self, obj):
        return format_html('<a href="{}">Ответить</a>',
                           reverse('send_admin_message', args=[obj.author.pk]))

    send_reply.short_description = 'Ответить'

    def send_message(self, obj):
        return format_html('<a href="{}">Отправить сообщение</a>',
                           reverse('send_admin_message', args=[obj.pk]))
    send_message.short_description = 'Сообщение'


class ServiceImagesWidget(RelatedFieldWidgetWrapper):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value:
            for img_id in value:
                image = Image.objects.get(pk=img_id)
                output.append(format_html('<img src="{}" height="100"/>', image.image.url))

        return mark_safe(''.join(output)) + super().render(name, value, attrs, renderer)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1  # Количество пустых форм для загрузки изображений


@admin.register(SimpleService)
class SimpleServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm

    list_display = ('id', 'name', 'price',)
    search_fields = ('name', 'description',)
    inlines = [ImageInline]  # Добавляем inline для изображений
    ordering = ('id', 'name', 'price')

    formfield_overrides = {
        models.ImageField: {'widget': AdminFileWidget},
    }


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'user', 'text', 'rating', 'created_at')
    search_fields = ('text', 'service__name', 'user__first_name', 'user__last_name')
    list_filter = ('service', 'rating', 'created_at')
    ordering = ('-created_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'user', 'text', 'answer')
    search_fields = ('text', 'service__name', 'user__first_name', 'user__last_name')
    list_filter = ('service',)
    ordering = ('-id',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text')
    search_fields = ('text', 'question__text')
    ordering = ('-id',)


@admin.register(Cemetery)
class CemeteryAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'address')
    search_fields = ('city__name', 'address')
    list_filter = ('city',)
    ordering = ('id', 'city', 'address')


@admin.register(CheckList)
class CheckListAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('id', 'name',)


@admin.register(ReviewExecuter)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'executor', 'created_at')
    search_fields = ('author__username', 'executor__username', 'content')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('executor', 'score')
    search_fields = ('executor__username', 'score')


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'rating')

from django.contrib import admin
from .models import ChatMessage, UserAccounts


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'created_at', 'is_read')
    actions = ['mark_as_read', 'reply_to_message']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Пометить как прочитанные"

    def reply_to_message(self, request, queryset):
        # Предполагаем, что queryset содержит только одно сообщение
        message = queryset.first()
        if message:
            # Перенаправляем на страницу ответа с ID сообщения
            reply_url = reverse('admin:reply_to_chat_message', args=[message.pk])
            return HttpResponseRedirect(reply_url)
        return HttpResponseRedirect(request.get_full_path())

    reply_to_message.short_description = "Ответить на сообщение"

    readonly_fields = ('author', 'text', 'created_at', 'is_read')
