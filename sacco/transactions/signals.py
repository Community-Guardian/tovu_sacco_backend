import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import (
    TransferTransaction,
    WithdrawTransaction,
    RefundTransaction,
    DepositTransaction,
)
from accounts.models import Account

# Configure logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=TransferTransaction)
@transaction.atomic
def update_balance_on_transfer(sender, instance, created, **kwargs):
    if instance.status != "completed":
        logger.info(f"Transfer transaction {instance.transaction_id} is not completed. Skipping balance update.")
        return
    if instance.is_processed:
        logger.info(f"Transfer transaction {instance.transaction_id} is already processed. Skipping balance update.")
        return

    try:
        sender_account = instance.sender_account
        receiver_account = instance.receiver_account
        amount = instance.amount

        # Validate accounts
        if not sender_account or not receiver_account:
            logger.warning(f"Transfer transaction {instance.transaction_id} failed: Missing accounts.")
            return

        # Perform balance update
        sender_account.account_balance -= amount
        receiver_account.account_balance += amount

        # Set is_processed to True
        instance.is_processed = True

        # save instance
        instance.save()

        # Save accounts
        sender_account.save()
        receiver_account.save()

        logger.info(f"Transfer transaction {instance.transaction_id} processed successfully.")
    except Exception as e:
        logger.error(f"Error processing transfer transaction {instance.transaction_id}: {str(e)}")
        raise


@receiver(post_save, sender=WithdrawTransaction)
@transaction.atomic
def update_balance_on_withdraw(sender, instance, created, **kwargs):
    if instance.status != "completed":
        logger.info(f"Withdraw transaction {instance.transaction_id} is not completed. Skipping balance update.")
        return
    if instance.is_processed:
        logger.info(f"Transfer transaction {instance.transaction_id} is already processed. Skipping balance update.")
        return
    try:
        account = instance.account
        amount = instance.amount

        # Validate account
        if not account:
            logger.warning(f"Withdraw transaction {instance.transaction_id} failed: Missing account.")
            return

        # Perform balance update
        account.account_balance -= amount
        
        # Set is_processed to True
        instance.is_processed = True

        # Save account
        account.save()

        # save instance
        instance.save()

        logger.info(f"Withdraw transaction {instance.transaction_id} processed successfully.")
    except Exception as e:
        logger.error(f"Error processing withdraw transaction {instance.transaction_id}: {str(e)}")
        raise


@receiver(post_save, sender=RefundTransaction)
@transaction.atomic
def update_balance_on_refund(sender, instance, created, **kwargs):
    if instance.status != "completed":
        logger.info(f"Refund transaction {instance.transaction_id} is not completed. Skipping balance update.")
        return
    if instance.is_processed:
        logger.info(f"Transfer transaction {instance.transaction_id} is already processed. Skipping balance update.")
        return
    try:
        account = instance.account
        amount = instance.amount

        # Perform balance update
        account.account_balance += amount
        
        # Set is_processed to True
        instance.is_processed = True

        # Save account
        account.save()

        # save instance
        instance.save()

        logger.info(f"Refund transaction {instance.transaction_id} processed successfully.")
    except Exception as e:
        logger.error(f"Error processing refund transaction {instance.transaction_id}: {str(e)}")
        raise


@receiver(post_save, sender=DepositTransaction)
@transaction.atomic
def update_balance_on_deposit(sender, instance, created, **kwargs):
    if instance.status != "completed":
        logger.info(f"Deposit transaction {instance.transaction_id} is not completed. Skipping balance update.")
        return
    if instance.is_processed:
        logger.info(f"Transfer transaction {instance.transaction_id} is already processed. Skipping balance update.")
        return
    try:
        account = instance.account
        amount = instance.amount

        # Validate account
        if not account:
            logger.warning(f"Deposit transaction {instance.transaction_id} failed: Missing account.")
            return

        # Perform balance update
        account.account_balance += amount
        
        # Set is_processed to True
        instance.is_processed = True

        # Save account
        account.save()

        # save instance
        instance.save()

        logger.info(f"Deposit transaction {instance.transaction_id} processed successfully.")
    except Exception as e:
        logger.error(f"Error processing deposit transaction {instance.transaction_id}: {str(e)}")
        raise
