import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import TransferTransaction, WithdrawTransaction, RefundTransaction, PaymentRequestTransaction, DepositTransaction
from accounts.models import Account

# Configure logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=TransferTransaction)
@transaction.atomic
def update_balance_on_transfer(sender, instance, created, **kwargs):
    if created:
        try:
            sender_account = instance.sender_account
            receiver_account = instance.receiver_account
            amount = instance.amount

            sender_account.account_balance -= amount
            receiver_account.account_balance += amount

            sender_account.save()
            receiver_account.save()

            logger.info(f"Transfer transaction {instance.transaction_id} processed successfully.")
        except Exception as e:
            logger.error(f"Error processing transfer transaction {instance.transaction_id}: {str(e)}")
            raise

@receiver(post_save, sender=WithdrawTransaction)
@transaction.atomic
def update_balance_on_withdraw(sender, instance, created, **kwargs):
    if created:
        try:
            account = instance.account
            amount = instance.amount

            account.account_balance -= amount
            account.save()

            logger.info(f"Withdraw transaction {instance.transaction_id} processed successfully.")
        except Exception as e:
            logger.error(f"Error processing withdraw transaction {instance.transaction_id}: {str(e)}")
            raise

@receiver(post_save, sender=RefundTransaction)
@transaction.atomic
def update_balance_on_refund(sender, instance, created, **kwargs):
    if created:
        try:
            account = instance.account
            amount = instance.amount

            account.account_balance += amount
            account.save()

            logger.info(f"Refund transaction {instance.transaction_id} processed successfully.")
        except Exception as e:
            logger.error(f"Error processing refund transaction {instance.transaction_id}: {str(e)}")
            raise

@receiver(post_save, sender=PaymentRequestTransaction)
@transaction.atomic
def update_balance_on_payment_request(sender, instance, created, **kwargs):
    if created and instance.status == "completed":
        try:
            account = instance.account
            amount = instance.amount

            account.account_balance += amount
            account.save()

            logger.info(f"Payment request transaction {instance.transaction_id} processed successfully.")
        except Exception as e:
            logger.error(f"Error processing payment request transaction {instance.transaction_id}: {str(e)}")
            raise

@receiver(post_save, sender=DepositTransaction)
@transaction.atomic
def update_balance_on_deposit(sender, instance, created, **kwargs):
    if created:
        try:
            account = instance.account
            amount = instance.amount

            account.account_balance += amount
            account.save()

            logger.info(f"Deposit transaction {instance.transaction_id} processed successfully.")
        except Exception as e:
            logger.error(f"Error processing deposit transaction {instance.transaction_id}: {str(e)}")
            raise