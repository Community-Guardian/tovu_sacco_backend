from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth import get_user_model
from accounts.models import Account
User = get_user_model()
# Define payment method choices
PAYMENT_METHODS = (
    ("mpesa", "M-Pesa"),
    ("paypal", "PayPal"),
    ("bank_transfer", "Bank Transfer"),
    ("other", "Other"),
)

TRANSACTION_TYPE = (
    ("transfer", "Transfer"),
    ("received", "Received"),
    ("withdraw", "Withdraw"),
    ("refund", "Refund"),
    ("deposit", "Deposit"),
    ("request", "Payment Request"),
    ("none", "None"),
)

TRANSACTION_STATUS = (
    ("failed", "Failed"),
    ("completed", "Completed"),
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("request_sent", "Request Sent"),
    ("request_settled", "Request Settled"),
    ("request_processing", "Request Processing"),
)

class BaseTransaction(models.Model):
    transaction_id = ShortUUIDField(unique=True, length=15, max_length=20, prefix="TRN")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(choices=TRANSACTION_STATUS, max_length=100, default="pending")
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=100, default="none")
    payment_method = models.CharField(choices=PAYMENT_METHODS, max_length=50, default="other")  # Payment method type
    # Fields specific to different payment methods
    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=False, null=True, blank=True)

    # Fields specific to different payment methods
    mpesa_result_code = models.CharField(max_length=100)
    mpesa_result_desc = models.CharField(max_length=100)    
    mpesa_merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_phone_number = models.CharField(max_length=15, blank=True, null=True)
    mpesa_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    paypal_transaction_id = models.CharField(max_length=100, null=True, blank=True)  # Specific to PayPal
    bank_transaction_ref = models.CharField(max_length=100, null=True, blank=True)  # Specific to Bank Transfer


    class Meta:
        abstract = True

class TransferTransaction(BaseTransaction):
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="received_transactions")
    sender_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="sender_account")
    receiver_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="receiver_account")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="transfer_transactions")

class WithdrawTransaction(BaseTransaction):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="withdraw_account")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="withdraw_transactions")

class RefundTransaction(BaseTransaction):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="refund_account")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="refund_transactions")

class PaymentRequestTransaction(BaseTransaction):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="payment_request_account")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="payment_request_transactions")

class DepositTransaction(BaseTransaction):
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="deposit_account")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="deposit_transactions")
