# sacco/transactions/models.py
from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth import get_user_model
from accounts.models import Account
from loans.models import Loan
from investments.models import Investment
from savings.models import Goal
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
User = get_user_model()

class AuditTransaction(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    transaction = GenericForeignKey('content_type', 'object_id')
    field_name = models.CharField(max_length=255)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Audit Transaction"
        verbose_name_plural = "Audit Transactions"
        ordering = ['-updated_at']

    def __str__(self):
        return f"Audit for {self.transaction} on {self.updated_at}"

class MpesaTransaction(models.Model):
    mpesa_checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    mpesa_phone_number = models.CharField(max_length=15, null=True, blank=True)
    mpesa_merchant_request_id = models.CharField(max_length=100, null=True, blank=True)
    mpesa_result_code = models.CharField(max_length=10, null=True, blank=True)
    mpesa_result_desc = models.CharField(max_length=255, null=True, blank=True)
    mpesa_transaction_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True

class BaseTransaction(models.Model):
    PAYMENT_METHODS = (
        ("mpesa", "M-Pesa"),
        ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"),
        ("in-house", "In-house"),
    )

    TRANSACTION_TYPE = (
        ("transfer", "Transfer"),
        ("received", "Received"),
        ("withdraw", "Withdraw"),
        ("refund", "Refund"),
        ("deposit", "Deposit"),
        ("loan", "Loan"),
        ("investment", "Investment"),
        ("saving", "Saving"),
    )

    TRANSACTION_STATUS = (
        ("failed", "Failed"),
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("processing", "Processing"),
    )

    transaction_id = ShortUUIDField(unique=True, length=15, max_length=20, prefix="TRN", db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_transactions", db_index=True)
    amount = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(choices=TRANSACTION_STATUS, max_length=100, default="pending", db_index=True)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHODS, max_length=50, default="in-house", db_index=True)
    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=False, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)
    audit_logs = GenericRelation(AuditTransaction)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.status == 'pending' and not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(days=3)
        super().save(*args, **kwargs)

class TransferTransaction(BaseTransaction):
    sender_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="sender_account")
    receiver_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="receiver_account")
    sender_goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, related_name="sender_goal")
    receiver_goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, related_name="receiver_goal")
class WithdrawTransaction(BaseTransaction, MpesaTransaction):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="withdraw_account")

class RefundTransaction(BaseTransaction, MpesaTransaction):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="refund_account")

class DepositTransaction(BaseTransaction, MpesaTransaction):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="deposit_account")

class LoanTransaction(BaseTransaction, MpesaTransaction):
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, related_name="loan_transactions")

class InvestmentTransaction(BaseTransaction, MpesaTransaction):
    investment = models.ForeignKey(Investment, on_delete=models.SET_NULL, null=True, related_name="investment_transactions")

class SavingTransaction(BaseTransaction, MpesaTransaction):
    goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, related_name="saving_transactions")

class MinimumSharesDepositTransaction(BaseTransaction, MpesaTransaction):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="minimum_shares_deposit_account")