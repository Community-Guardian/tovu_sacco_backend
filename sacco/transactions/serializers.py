from rest_framework import serializers
from .models import BaseTransaction, TransferTransaction, WithdrawTransaction, RefundTransaction, DepositTransaction
from accounts.models import Account
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for BaseTransaction model. 
    This includes the common fields for all transaction types.
    """
    status = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_STATUS, default="pending")
    transaction_type = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_TYPE, default="transfer")
    payment_method = serializers.ChoiceField(choices=BaseTransaction.PAYMENT_METHODS, default="in-house")

    class Meta:
        model = BaseTransaction
        fields = '__all__'  # Include all fields from BaseTransaction


class TransferTransactionSerializer(serializers.ModelSerializer):
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    sender_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    receiver_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    status = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_STATUS, default="pending")
    transaction_type = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_TYPE, default="transfer")

    class Meta:
        model = TransferTransaction
        fields = '__all__'  # Include all fields from TransferTransaction

    def create(self, validated_data):
        """
        Override the create method to add the user field during creation.
        """
        user = self.context['request'].user  # Access the user from request context
        validated_data['user'] = user  # Add the user to the validated data
        
        return super().create(validated_data)  # Proceed with the original create method


class WithdrawTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    status = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_STATUS, default="pending")
    transaction_type = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_TYPE, default="withdraw")

    class Meta:
        model = WithdrawTransaction
        fields = '__all__'  # Include all fields from WithdrawTransaction

    def create(self, validated_data):
        user = self.context['request'].user  # Access the user from request context
        validated_data['user'] = user  # Add the user to the validated data
        
        return super().create(validated_data)  # Proceed with the original create method


class RefundTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    status = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_STATUS, default="pending")
    transaction_type = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_TYPE, default="refund")

    class Meta:
        model = RefundTransaction
        fields = '__all__'  # Include all fields from RefundTransaction

    def create(self, validated_data):
        user = self.context['request'].user  # Access the user from request context
        validated_data['user'] = user  # Add the user to the validated data
        
        return super().create(validated_data)  # Proceed with the original create method


class DepositTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    status = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_STATUS , default="pending")
    transaction_type = serializers.ChoiceField(choices=BaseTransaction.TRANSACTION_TYPE ,default="deposit")

    class Meta:
        model = DepositTransaction
        fields = '__all__'  # Include all fields from DepositTransaction

    def create(self, validated_data):
        user = self.context['request'].user  # Access the user from request context
        validated_data['user'] = user  # Add the user to the validated data
        
        return super().create(validated_data)  # Proceed with the original create method