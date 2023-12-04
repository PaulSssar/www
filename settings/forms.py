from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import EmailSettings


class EmailSettingsForm(ModelForm):
    class Meta:
        model = EmailSettings
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        email_use_tls = cleaned_data.get("email_use_tls")
        email_use_ssl = cleaned_data.get("email_use_ssl")
        if email_use_tls and email_use_ssl:
            raise ValidationError(
                "EMAIL_USE_TLS и EMAIL_USE_SSL взаимоисключающие, поэтому установите только один из этих параметров в True.")
        return cleaned_data
