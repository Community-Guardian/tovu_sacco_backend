from rest_framework import serializers
from .models import Account, KYC


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Account model.
    """
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['id', 'account_number', 'account_id', 'pin_number', 'red_code', 'date', 'user']


class KYCSerializer(serializers.ModelSerializer):
    """
    Serializer for the KYC model.
    """
    class Meta:
        model = KYC
        fields = '__all__'
        read_only_fields = ['id', 'account', 'user', 'date']
