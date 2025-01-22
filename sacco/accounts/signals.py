import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Account, KYC
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Account)
def check_kyc_before_account_creation(sender, instance, **kwargs):
    """
    Before creating an Account, ensure the user has submitted KYC.
    If not, raise an error to request KYC submission.
    """
    try:
        if not KYC.objects.filter(user=instance.user).exists():
            logger.warning(f"KYC information is required for user {instance.user.id} before creating an account.")
            raise ValidationError("KYC information is required before creating an account. Please submit your KYC first.")
    except Exception as e:
        logger.error(f"Error in check_kyc_before_account_creation: {str(e)}")
        raise

@receiver(pre_save, sender=KYC)
def check_existing_kyc(sender, instance, **kwargs):
    """
    Before creating a KYC entry, check if the user already has one.
    If a KYC record exists, raise an error to request editing instead.
    """
    try:
        if KYC.objects.filter(user=instance.user).exists() and not instance.pk:
            logger.warning(f"KYC record already exists for user {instance.user.id}.")
            raise ValidationError("KYC record already exists. Please edit the existing KYC information instead.")
    except Exception as e:
        logger.error(f"Error in check_existing_kyc: {str(e)}")
        raise

@receiver(post_save, sender=KYC)
def link_kyc_to_account(sender, instance, created, **kwargs):
    """
    Once a KYC is created or updated, link it to the user's account if it exists.
    """
    try:
        account = Account.objects.filter(user=instance.user).first()
        if account and not account.kyc_submitted:
            account.kyc_submitted = True
            account.save()
            logger.info(f"Linked KYC {instance.id} to account {account.id}.")
    except Exception as e:
        logger.error(f"Error in link_kyc_to_account: {str(e)}")
        raise

@receiver(post_save, sender=Account)
def update_account_status_on_kyc_confirmation(sender, instance, **kwargs):
    """
    Update the account status when KYC is confirmed.
    """
    try:
        if instance.kyc_confirmed and instance.account_status == "in-active":
            instance.account_status = "active"
            instance.save()
            logger.info(f"Updated account status to 'active' for account {instance.id}.")
    except Exception as e:
        logger.error(f"Error in update_account_status_on_kyc_confirmation: {str(e)}")
        raise