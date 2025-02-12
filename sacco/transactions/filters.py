import django_filters
from .models import (
    TransferTransaction, WithdrawTransaction, RefundTransaction,
    DepositTransaction, LoanTransaction, InvestmentTransaction,
    SavingTransaction, MinimumSharesDepositTransaction
)

class BaseTransactionFilter(django_filters.FilterSet):
    """
    Base filter for transactions.
    Allows filtering by amount, status, transaction type, payment method, and date range.
    """
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    status = django_filters.ChoiceFilter(choices=[("failed", "Failed"), ("completed", "Completed"), ("pending", "Pending"), ("processing", "Processing")])
    transaction_type = django_filters.ChoiceFilter(choices=[
        ("transfer", "Transfer"), ("received", "Received"), ("withdraw", "Withdraw"),
        ("refund", "Refund"), ("deposit", "Deposit"), ("loan", "Loan"),
        ("investment", "Investment"), ("saving", "Saving")
    ])
    payment_method = django_filters.ChoiceFilter(choices=[
        ("mpesa", "M-Pesa"), ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"), ("in-house", "In-house")
    ])
    start_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="lte")

    class Meta:
        fields = ["amount", "status", "transaction_type", "payment_method", "date"]

class TransferTransactionFilter(BaseTransactionFilter):
    sender_account = django_filters.NumberFilter(field_name="sender_account__id")
    receiver_account = django_filters.NumberFilter(field_name="receiver_account__id")
    sender_goal = django_filters.NumberFilter(field_name="sender_goal__id")
    receiver_goal = django_filters.NumberFilter(field_name="receiver_goal__id")

    class Meta:
        model = TransferTransaction
        fields = BaseTransactionFilter.Meta.fields + ["sender_account", "receiver_account", "sender_goal", "receiver_goal"]

class WithdrawTransactionFilter(BaseTransactionFilter):
    account = django_filters.NumberFilter(field_name="account__id")

    class Meta:
        model = WithdrawTransaction
        fields = BaseTransactionFilter.Meta.fields + ["account"]

class RefundTransactionFilter(BaseTransactionFilter):
    account = django_filters.NumberFilter(field_name="account__id")

    class Meta:
        model = RefundTransaction
        fields = BaseTransactionFilter.Meta.fields + ["account"]

class DepositTransactionFilter(BaseTransactionFilter):
    account = django_filters.NumberFilter(field_name="account__id")

    class Meta:
        model = DepositTransaction
        fields = BaseTransactionFilter.Meta.fields + ["account"]

class LoanTransactionFilter(BaseTransactionFilter):
    loan = django_filters.NumberFilter(field_name="loan__id")

    class Meta:
        model = LoanTransaction
        fields = BaseTransactionFilter.Meta.fields + ["loan"]

class InvestmentTransactionFilter(BaseTransactionFilter):
    investment = django_filters.NumberFilter(field_name="investment__id")

    class Meta:
        model = InvestmentTransaction
        fields = BaseTransactionFilter.Meta.fields + ["investment"]

class SavingTransactionFilter(BaseTransactionFilter):
    goal = django_filters.NumberFilter(field_name="goal__id")

    class Meta:
        model = SavingTransaction
        fields = BaseTransactionFilter.Meta.fields + ["goal"]

class MinimumSharesDepositTransactionFilter(BaseTransactionFilter):
    account = django_filters.NumberFilter(field_name="account__id")

    class Meta:
        model = MinimumSharesDepositTransaction
        fields = BaseTransactionFilter.Meta.fields + ["account"]
