from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account,KYC
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail

@receiver(post_save, sender=Account)
def account_created(sender, instance, created, **kwargs):
    if created:
        # Ensure that the KYC information is linked to the account
        if not instance.kyc:
            raise ValidationError("Account must be linked to a valid KYC.")
    # Send an email to the user after account creation
        send_email_notification(instance.user.email)

def send_email_notification(user_email):
    name = settings.SITENAME
    subject = "Account Created Successfully"
    message = "Hello, your account has been created successfully. Welcome to our " + name + " platform!"
    from_email = settings.EMAIL_HOST_USER  
    
    send_mail(
        subject,
        message,
        from_email,
        [user_email],
        fail_silently=False,
    )
@receiver(post_save, sender=KYC)
def kyc_created(sender, instance, created, **kwargs):
    if created:
        # Create an account automatically when KYC is created
        Account.objects.get_or_create(user=instance.user, kyc=instance)
