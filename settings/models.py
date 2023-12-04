from django.conf import settings
from django.core.mail import send_mail
from django.db import models


class EmailSettings(models.Model):
    """Модель настроек почты"""
    email_host = models.CharField(max_length=1024, verbose_name='Email Host', default='smtp.example.com')
    email_host_user = models.CharField(max_length=255, verbose_name='Email Host User', default='user@example.com')
    email_host_password = models.CharField(max_length=255, verbose_name='Email Host Password')
    email_port = models.IntegerField(verbose_name='Email Port', default=587)
    email_use_tls = models.BooleanField(verbose_name='Use TLS', default=True)
    email_use_ssl = models.BooleanField(verbose_name='Use SSL', default=False)

    def __str__(self):
        return f"Настройки почты для {self.email_host_user}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # После сохранения отправляем тестовое письмо
        self.send_test_email()

    def send_test_email(self):
        print("Отправка тестового письма")
        # Настройка параметров почтового сервера
        settings.EMAIL_HOST = self.email_host
        settings.EMAIL_HOST_USER = self.email_host_user
        settings.EMAIL_HOST_PASSWORD = self.email_host_password
        settings.EMAIL_PORT = self.email_port
        settings.EMAIL_USE_TLS = self.email_use_tls
        settings.EMAIL_USE_SSL = self.email_use_ssl
        print(f"Настройки почты изменены: {settings.EMAIL_HOST_USER}")
        print(f"Настройки почты изменены: {settings.EMAIL_HOST_PASSWORD}")
        print(f"Настройки почты изменены: {settings.EMAIL_PORT}")
        print(f"Настройки почты изменены TLS: {settings.EMAIL_USE_TLS}")
        print(f"Настройки почты изменены SSL: {settings.EMAIL_USE_SSL}")

        # Отправка тестового письма
        try:
            send_mail(
                'Тестовое письмо',
                'Это тестовое письмо, отправленное для проверки настроек почты.',
                self.email_host_user,
                [self.email_host_user, "nickolayvan@gmail.com"],
                fail_silently=False,
            )
            print('Тестовое письмо успешно отправлено.')
        except Exception as e:
            print(f'Ошибка при отправке тестового письма: {e}')

    class Meta:
        verbose_name = 'Настройку почты'
        verbose_name_plural = 'Настройки почты'
