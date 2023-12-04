from django.core.mail import send_mail
from django.conf import settings
from .models import EmailSettings


def send_test_email(recipient_email):
    """Отправка тестового письма"""
    email_settings = EmailSettings.objects.first()  # предполагается, что у вас только один набор настроек
    if not email_settings:
        raise ValueError('Email settings have not been configured.')

    settings.EMAIL_HOST = email_settings.email_host
    settings.EMAIL_HOST_USER = email_settings.email_host_user
    settings.EMAIL_HOST_PASSWORD = email_settings.email_host_password
    settings.EMAIL_PORT = email_settings.email_port
    settings.EMAIL_USE_TLS = email_settings.email_use_tls
    settings.EMAIL_USE_SSL = email_settings.email_use_ssl

    send_mail(
        'Test Email',
        'This is a test email.',
        settings.EMAIL_HOST_USER,
        [recipient_email, "nickolayvan@gmail.com"],
        fail_silently=False,
    )
