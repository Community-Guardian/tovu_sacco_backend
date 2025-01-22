from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import KYC, Account

# Signal to mark KYC as submitted after it's created
@receiver(post_save, sender=KYC)
def mark_kyc_submitted(sender, instance, created, **kwargs):
    if created:
        # Automatically mark the KYC as submitted upon creation
        instance.kyc_submitted = True
        instance.save()

# Signal to add KYC to account when account is created
@receiver(post_save, sender=Account)
def link_kyc_to_account(sender, instance, created, **kwargs):
    if created:
        # Check if the user has a KYC
        try:
            kyc = KYC.objects.get(user=instance.user)
            # Add KYC to the account
            instance.kyc= kyc
        except KYC.DoesNotExist:
            pass  # If no KYC exists, it will silently pass. You can log if needed.
