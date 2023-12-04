from django.contrib import admin
from settings.forms import EmailSettingsForm

from .models import EmailSettings


@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    form = EmailSettingsForm
    list_display = ('email_host', 'email_host_user', 'email_port', 'email_use_tls', 'email_use_ssl')
    fields = ('email_host', 'email_host_user', 'email_host_password', 'email_port', 'email_use_tls', 'email_use_ssl')
