from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор платежа"""
    class Meta:
        model = Payment
        fields = ['amount', 'order']

    def create(self, validated_data):
        return Payment.objects.create(**validated_data)
