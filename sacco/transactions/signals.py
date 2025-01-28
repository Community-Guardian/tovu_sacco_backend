from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
import logging
from django.db import transaction
from .models import (
    BaseTransaction,
    TransferTransaction,
    WithdrawTransaction,
    RefundTransaction,
    DepositTransaction,
    AuditTransaction
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

User = get_user_model()
@receiver(pre_save, sender=BaseTransaction)
def track_transaction_changes(sender, instance, **kwargs):
    """
    Signal to track changes made to a transaction.
    This will log changes to the AuditTransaction model.
    """
    if instance.pk:  # If it's an existing transaction (not a new one)
        try:
            # Get the previous transaction object
            previous_transaction = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            logger.warning(f"Previous transaction with pk={instance.pk} does not exist.")
            return  # No previous transaction exists

        # Compare the fields for changes
        for field in sender._meta.fields:
            field_name = field.name
            new_value = getattr(instance, field_name)
            old_value = getattr(previous_transaction, field_name)

            if old_value != new_value:
                try:
                    # Log the change in the AuditTransaction model
                    AuditTransaction.objects.create(
                        transaction=instance,
                        field_name=field_name,
                        old_value=str(old_value),
                        new_value=str(new_value),
                        updated_by=instance.user if instance.user else None,
                        updated_at=now(),
                    )
                    logger.info(
                        f"Field '{field_name}' changed in transaction {instance.pk}. "
                        f"Old value: {old_value}, New value: {new_value}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to log change for field '{field_name}' in transaction {instance.pk}: {str(e)}"
                    )


def create_audit_log(transaction, created=False, updated_fields=None, user=None):
    """
    Helper function to create audit logs for a transaction.

    :param transaction: The transaction instance
    :param created: Whether the transaction is newly created
    :param updated_fields: Dictionary of updated fields with old and new values
    :param user: The user responsible for the update (if applicable)
    """
    try:
        for field in transaction._meta.fields:
            field_name = field.name
            value = getattr(transaction, field_name)

            if created or (updated_fields and field_name in updated_fields):
                AuditTransaction.objects.create(
                    transaction=transaction,
                    field_name=field_name,
                    old_value="N/A" if created else str(updated_fields[field_name]["old"]),
                    new_value=str(value),
                    updated_by=user or transaction.user,
                    updated_at=now(),
                )
    except Exception as e:
        logger.error(f"Error creating audit log for transaction {transaction.pk}: {str(e)}")
@receiver(post_save, sender=TransferTransaction)
def audit_transfer_transaction(sender, instance, created, **kwargs):
    if created:
        # Log the creation of the transaction
        create_audit_log(instance, created=True)
    else:
        # Log updates to the transaction
        updated_fields = {
            field.name: {
                "old": getattr(sender.objects.get(pk=instance.pk), field.name),
                "new": getattr(instance, field.name),
            }
            for field in instance._meta.fields
            if getattr(instance, field.name) != getattr(sender.objects.get(pk=instance.pk), field.name)
        }
        create_audit_log(instance, updated_fields=updated_fields)
@receiver(post_save, sender=WithdrawTransaction)
def audit_withdraw_transaction(sender, instance, created, **kwargs):
    if created:
        create_audit_log(instance, created=True)
    else:
        updated_fields = {
            field.name: {
                "old": getattr(sender.objects.get(pk=instance.pk), field.name),
                "new": getattr(instance, field.name),
            }
            for field in instance._meta.fields
            if getattr(instance, field.name) != getattr(sender.objects.get(pk=instance.pk), field.name)
        }
        create_audit_log(instance, updated_fields=updated_fields)

@receiver(post_save, sender=DepositTransaction)
def audit_deposit_transaction(sender, instance, created, **kwargs):
    if created:
        create_audit_log(instance, created=True)
    else:
        updated_fields = {
            field.name: {
                "old": getattr(sender.objects.get(pk=instance.pk), field.name),
                "new": getattr(instance, field.name),
            }
            for field in instance._meta.fields
            if getattr(instance, field.name) != getattr(sender.objects.get(pk=instance.pk), field.name)
        }
        create_audit_log(instance, updated_fields=updated_fields)

@receiver(post_save, sender=RefundTransaction)
def audit_refund_transaction(sender, instance, created, **kwargs):
    if created:
        create_audit_log(instance, created=True)
    else:
        updated_fields = {
            field.name: {
                "old": getattr(sender.objects.get(pk=instance.pk), field.name),
                "new": getattr(instance, field.name),
            }
            for field in instance._meta.fields
            if getattr(instance, field.name) != getattr(sender.objects.get(pk=instance.pk), field.name)
        }
        create_audit_log(instance, updated_fields=updated_fields)