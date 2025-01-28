from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth import get_user_model
from accounts.models import Account
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

User = get_user_model()



class BaseTransaction(models.Model):
    """
    Base model for all transaction types. Contains common fields for tracking the transaction.
    """
    # Define payment method choices
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
        ("request", "Payment Request"),
    )

    TRANSACTION_STATUS = (
        ("failed", "Failed"),
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("processing", "Processing"),
    )
    transaction_id = ShortUUIDField(unique=True, length=15, max_length=20, prefix="TRN", db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="transactions", db_index=True)
    amount = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(choices=TRANSACTION_STATUS, max_length=100, default="pending", db_index=True)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHODS, max_length=50, default="in-house", db_index=True)  
    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=False, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)  # Transaction expiry field
    audit_logs = GenericRelation('AuditTransaction')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Automatically set the expiry date for pending transactions
        if self.status == 'pending' and not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(days=3)  # Set expiry after 3 days
        super().save(*args, **kwargs)

    @property
    def net_amount(self):
        # This can be used to calculate the net amount after applying fees/discounts
        return self.amount - self.transaction_fee - self.discount

    def clean(self):
        # Custom validation example: Ensure M-Pesa is not used for refund transactions
        if self.payment_method == 'mpesa' and self.transaction_type == 'refund':
            raise ValidationError("M-Pesa cannot be used for refund transactions.")

class MpesaTransaction(models.Model):
    """
    Stores M-Pesa specific transaction data.
    """
    # transaction = models.OneToOneField(BaseTransaction, on_delete=models.CASCADE,related_name="mpesa_transaction")
    mpesa_result_code = models.CharField(max_length=100, blank=True, null=True)
    mpesa_result_desc = models.CharField(max_length=100, blank=True, null=True)    
    mpesa_merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_phone_number = models.CharField(max_length=15, blank=True, null=True)
    mpesa_transaction_id = models.CharField(max_length=100, blank=True, null=True)

    # class Meta:
    #     abstract = True

class PaypalTransaction(models.Model):
    """
    Stores PayPal specific transaction data.
    """
    # transaction = models.OneToOneField(BaseTransaction, on_delete=models.CASCADE,related_name="paypal_transaction")
    paypal_transaction_id = models.CharField(max_length=100, null=True, blank=True)

    # class Meta:
    #     abstract = True

class BankTransaction(models.Model):
    """
    Stores Bank Transfer specific transaction data.
    """
    # transaction = models.OneToOneField(BaseTransaction, on_delete=models.CASCADE,related_name="bank_transaction")
    bank_transaction_ref = models.CharField(max_length=100, null=True, blank=True)

    # class Meta:
    #     abstract = True

class TransferTransaction(BaseTransaction):
    """
    Handles transfer transactions between users, including relevant payment method data.
    """
    sender_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="sender_account")
    receiver_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="receiver_account")
    mpesa_transaction = models.OneToOneField(MpesaTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfer_mpesa_transaction")
    paypal_transaction = models.OneToOneField(PaypalTransaction, on_delete=models.SET_NULL, null=True, blank=True , related_name="transfer_paypal_transaction")
    bank_transaction = models.OneToOneField(BankTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfer_bank_transaction")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="transfer_transactions")

class WithdrawTransaction(BaseTransaction):
    """
    Handles withdrawal transactions, including relevant payment method data.
    """
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="withdraw_account")
    mpesa_transaction = models.OneToOneField(MpesaTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="withdraw_mpesa_transaction")
    paypal_transaction = models.OneToOneField(PaypalTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="withdraw_paypal_transaction")
    bank_transaction = models.OneToOneField(BankTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="withdraw_bank_transaction")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="withdraw_transactions")

    class Meta:
        verbose_name = "Withdrawal Transaction"

    def save(self, *args, **kwargs):
        # Call clean to validate before saving
        print(self.account.account_balance)
        if self.account and not self.is_processed and self.amount > self.account.account_balance:
            raise ValidationError("Withdrawal amount cannot exceed account balance.")
        super().save(*args, **kwargs)
class RefundTransaction(BaseTransaction):
    """
    Handles refund transactions, including relevant payment method data.
    """
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="refund_account")
    mpesa_transaction = models.OneToOneField(MpesaTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="refund_mpesa_transaction")
    paypal_transaction = models.OneToOneField(PaypalTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="refund_paypal_transaction")
    bank_transaction = models.OneToOneField(BankTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="refund_bank_transaction")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="refund_transactions")

class DepositTransaction(BaseTransaction):
    """
    Handles deposit transactions, including relevant payment method data.
    """
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="deposit_account")
    mpesa_transaction = models.OneToOneField(MpesaTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="deposit_mpesa_transaction")
    paypal_transaction = models.OneToOneField(PaypalTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="deposit_paypal_transaction")
    bank_transaction = models.OneToOneField(BankTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="deposit_bank_transaction")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="deposit_transactions")

# Custom manager for filtering common queries
class TransactionManager(models.Manager):
    """
    Custom manager for filtering transactions by status.
    """
    def completed(self):
        return self.filter(status="completed")

    def pending(self):
        return self.filter(status="pending")

    def failed(self):
        return self.filter(status="failed")

# Adding custom manager to BaseTransaction for convenience
BaseTransaction.add_to_class('objects', TransactionManager())

class AuditTransaction(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    transaction = GenericForeignKey('content_type', 'object_id')
    
    field_name = models.CharField(max_length=100)
    old_value = models.TextField()
    new_value = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
