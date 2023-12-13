from django.contrib import admin
from pay.models import PaymentSettings, Payment


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'amount', 'created_at', 'payment_url', 'order')
    list_filter = ('status', 'created_at', 'order')
    ordering = ('id', 'status', 'amount', 'created_at')
    search_fields = ('status', 'amount', 'order__id')  # предполагается, что 'order' это ForeignKey
    readonly_fields = ('created_at', 'updated_at', 'payment_url', 'order')

    # Убедитесь, что у вас есть 'created_at', 'updated_at', 'payment_url', 'order' поля в модели Payment
    fieldsets = (
        (None, {'fields': ('status', 'amount', 'created_at', 'updated_at', 'payment_url', 'order')}),
    )
