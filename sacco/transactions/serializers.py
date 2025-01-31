from rest_framework import serializers
from .models import TransferTransaction, WithdrawTransaction, RefundTransaction, DepositTransaction, LoanTransaction, InvestmentTransaction, SavingTransaction, MinimumSharesDepositTransaction, AuditTransaction
from accounts.models import Account
from loans.models import Loan
from investments.models import Investment
from savings.models import Goal
from userManager.serializers import CustomUserSerializer

class TransferTransactionSerializer(serializers.ModelSerializer):
    sender_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)
    receiver_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)
    sender_goal = serializers.PrimaryKeyRelatedField(queryset=Goal.objects.all(), required=False)
    receiver_goal = serializers.PrimaryKeyRelatedField(queryset=Goal.objects.all(), required=False)
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = TransferTransaction
        fields = '__all__'


class WithdrawTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = WithdrawTransaction
        fields = '__all__'

class RefundTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = RefundTransaction
        fields = '__all__'

class DepositTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = DepositTransaction
        fields = '__all__'

class LoanTransactionSerializer(serializers.ModelSerializer):
    loan = serializers.PrimaryKeyRelatedField(queryset=Loan.objects.all())
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = LoanTransaction
        fields = '__all__'

class InvestmentTransactionSerializer(serializers.ModelSerializer):
    investment = serializers.PrimaryKeyRelatedField(queryset=Investment.objects.all())
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = InvestmentTransaction
        fields = '__all__'

class SavingTransactionSerializer(serializers.ModelSerializer):
    goal = serializers.PrimaryKeyRelatedField(queryset=Goal.objects.all())
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = SavingTransaction
        fields = '__all__'

class MinimumSharesDepositTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = MinimumSharesDepositTransaction
        fields = '__all__'

class AuditTransactionSerializer(serializers.ModelSerializer):
    transaction = serializers.SerializerMethodField()
    updated_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = AuditTransaction
        fields = '__all__'

    def get_transaction(self, obj):
        if isinstance(obj.transaction, TransferTransaction):
            return TransferTransactionSerializer(obj.transaction).data
        elif isinstance(obj.transaction, WithdrawTransaction):
            return WithdrawTransactionSerializer(obj.transaction).data
        elif isinstance(obj.transaction, RefundTransaction):
            return RefundTransactionSerializer(obj.transaction).data
        elif isinstance(obj.transaction, DepositTransaction):
            return DepositTransactionSerializer(obj.transaction).data
        elif isinstance(obj.transaction, LoanTransaction):
            return LoanTransactionSerializer(obj.transaction).data
        elif isinstance(obj.transaction, InvestmentTransaction):
            return InvestmentTransactionSerializer(obj.transaction).data
        elif isinstance(obj.transaction, SavingTransaction):
            return SavingTransactionSerializer(obj.transaction).data
        elif isinstance(obj.transaction, MinimumSharesDepositTransaction):
            return MinimumSharesDepositTransactionSerializer(obj.transaction).data
        return None