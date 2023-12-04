from django.urls import path
from .views import CreatePaymentView, PaymentWebhookView, PaymentStatusView

urlpatterns = [
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('payment/webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('payment/status/', PaymentStatusView.as_view(), name='payment-status'),
]