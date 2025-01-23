from rest_framework import serializers
from .models import TransferTransaction, WithdrawTransaction, RefundTransaction, DepositTransaction

class TransferTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferTransaction
        fields = '__all__'

class WithdrawTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawTransaction
        fields = '__all__'

class RefundTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundTransaction
        fields = '__all__'


class DepositTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositTransaction
        fields = '__all__'