# import logging
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.db import transaction
# from .models import (
#     TransferTransaction,
#     WithdrawTransaction,
#     RefundTransaction,
#     DepositTransaction,
# )
# from accounts.models import Account

# # Configure logging
# logger = logging.getLogger(__name__)


# @receiver(post_save, sender=TransferTransaction)
# @transaction.atomic
# def update_balance_on_transfer(sender, instance, created, **kwargs):
#     if instance.status != "completed":
#         logger.info(f"Transfer transaction {instance.transaction_id} is not completed. Skipping balance update.")
#         return
#     if instance.is_processed:
#         logger.info(f"Transfer transaction {instance.transaction_id} is already processed. Skipping balance update.")
#         return

#     try:
#         sender_account = instance.sender_account
#         receiver_account = instance.receiver_account
#         amount = instance.amount

#         # Validate accounts
#         if not sender_account or not receiver_account:
#             logger.warning(f"Transfer transaction {instance.transaction_id} failed: Missing accounts.")
#             return

#         # Perform balance update
#         sender_account.account_balance -= amount
#         receiver_account.account_balance += amount

#         # Set is_processed to True
#         instance.is_processed = True

#         # save instance
#         instance.save()

#         # Save accounts
#         sender_account.save()
#         receiver_account.save()

#         logger.info(f"Transfer transaction {instance.transaction_id} processed successfully.")
#     except Exception as e:
#         logger.error(f"Error processing transfer transaction {instance.transaction_id}: {str(e)}")
#         raise


# @receiver(post_save, sender=WithdrawTransaction)
# @transaction.atomic
# def update_balance_on_withdraw(sender, instance, created, **kwargs):
#     if instance.status != "completed":
#         logger.info(f"Withdraw transaction {instance.transaction_id} is not completed. Skipping balance update.")
#         return
#     if instance.is_processed:
#         logger.info(f"Transfer transaction {instance.transaction_id} is already processed. Skipping balance update.")
#         return
#     try:
#         account = instance.account
#         amount = instance.amount

#         # Validate account
#         if not account:
#             logger.warning(f"Withdraw transaction {instance.transaction_id} failed: Missing account.")
#             return

#         # Perform balance update
#         account.account_balance -= amount
        
#         # Set is_processed to True
#         instance.is_processed = True

#         # Save account
#         account.save()

#         # save instance
#         instance.save()

#         logger.info(f"Withdraw transaction {instance.transaction_id} processed successfully.")
#     except Exception as e:
#         logger.error(f"Error processing withdraw transaction {instance.transaction_id}: {str(e)}")
#         raise


# @receiver(post_save, sender=RefundTransaction)
# @transaction.atomic
# def update_balance_on_refund(sender, instance, created, **kwargs):
#     if instance.status != "completed":
#         logger.info(f"Refund transaction {instance.transaction_id} is not completed. Skipping balance update.")
#         return
#     if instance.is_processed:
#         logger.info(f"Transfer transaction {instance.transaction_id} is already processed. Skipping balance update.")
#         return
#     try:
#         account = instance.account
#         amount = instance.amount

#         # Perform balance update
#         account.account_balance += amount
        
#         # Set is_processed to True
#         instance.is_processed = True

#         # Save account
#         account.save()

#         # save instance
#         instance.save()

#         logger.info(f"Refund transaction {instance.transaction_id} processed successfully.")
#     except Exception as e:
#         logger.error(f"Error processing refund transaction {instance.transaction_id}: {str(e)}")
#         raise


# @receiver(post_save, sender=DepositTransaction)
# @transaction.atomic
# def update_balance_on_deposit(sender, instance, created, **kwargs):
#     if instance.status != "completed":
#         logger.info(f"Deposit transaction {instance.transaction_id} is not completed. Skipping balance update.")
#         return
#     if instance.is_processed:
#         logger.info(f"Transfer transaction {instance.transaction_id} is already processed. Skipping balance update.")
#         return
#     try:
#         account = instance.account
#         amount = instance.amount

#         # Validate account
#         if not account:
#             logger.warning(f"Deposit transaction {instance.transaction_id} failed: Missing account.")
#             return

#         # Perform balance update
#         account.account_balance += amount
        
#         # Set is_processed to True
#         instance.is_processed = True

#         # Save account
#         account.save()

#         # save instance
#         instance.save()

#         logger.info(f"Deposit transaction {instance.transaction_id} processed successfully.")
#     except Exception as e:
#         logger.error(f"Error processing deposit transaction {instance.transaction_id}: {str(e)}")
#         raise
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import BaseTransaction, AuditTransaction
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

User = get_user_model()

# Signal to track changes in transactions
@receiver(pre_save, sender=BaseTransaction)
def track_transaction_changes(sender, instance, **kwargs):
    """
    Signal to track changes made to a transaction.
    This will log changes to the AuditTransaction model.
    """
    if instance.pk:  # If it's an existing transaction (not a new one)
        # Get the previous transaction object
        try:
            previous_transaction = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return  # No previous transaction exists

        # Compare the fields for changes
        for field in sender._meta.fields:
            field_name = field.name
            new_value = getattr(instance, field_name)
            old_value = getattr(previous_transaction, field_name)

            if old_value != new_value:
                # Log the change in the AuditTransaction model
                AuditTransaction.objects.create(
                    transaction=instance,
                    field_name=field_name,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    updated_by=instance.user if instance.user else None,  # Use user if available
                    updated_at=now()
                )

# Signal to track new transactions (creating audit log on creation)
@receiver(post_save, sender=BaseTransaction)
def create_audit_log_on_creation(sender, instance, created, **kwargs):
    """
    Signal to create an audit log when a new transaction is created.
    """
    if created:
        # Log the initial creation of the transaction
        for field in sender._meta.fields:
            field_name = field.name
            new_value = getattr(instance, field_name)

            # Create an audit log for each field on creation
            AuditTransaction.objects.create(
                transaction=instance,
                field_name=field_name,
                old_value='N/A',  # No previous value
                new_value=str(new_value),
                updated_by=instance.user if instance.user else None,
                updated_at=now()
            )