from .models import SimpleService, ChatMessage

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm


class ServiceAdminForm(ModelForm):
    class Meta:
        model = SimpleService
        exclude = ('images',)
        widgets = {
            'cities': FilteredSelectMultiple("Города", is_stacked=False),
            'additional_services': FilteredSelectMultiple("Дополнительные услуги", is_stacked=False),
        }


class AdminChatMessageForm(ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['text']

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        self.recipient = kwargs.pop('recipient', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super().save(commit=False)
        if self.author:
            message.author = self.author
        if self.recipient:
            message.recipient = self.recipient
        if commit:
            message.save()
        return message
