from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserNotification, AdminNotification
from accounts.models import Account, KYC, NextOfKin
from savings.models import Goal, SavingMilestone, SavingReminder
from investments.models import Investment, UserInvestment, Dividend
from loans.models import Loan, LoanPayment

User = get_user_model()

@receiver(post_save, sender=Account)
def create_account_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.user,
            account=instance,
            title="Account Created",
            message="Your account has been successfully created.",
            notification_type="success",
            user_action="account_creation"
        )

@receiver(post_save, sender=KYC)
def create_kyc_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="KYC Submitted",
            message="Your KYC information has been submitted.",
            notification_type="info",
            user_action="kyc_submission"
        )

@receiver(post_save, sender=NextOfKin)
def create_next_of_kin_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="Next of Kin Added",
            message="A new next of kin has been added to your account.",
            notification_type="info",
            user_action="next_of_kin_added"
        )

@receiver(post_save, sender=Goal)
def create_goal_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="New Goal Created",
            message=f"A new goal '{instance.name}' has been created.",
            notification_type="info",
            user_action="goal_creation"
        )

@receiver(post_save, sender=SavingMilestone)
def create_milestone_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.goal.account.user,
            account=instance.goal.account,
            title="Milestone Created",
            message=f"A new milestone of {instance.milestone_amount} has been set for your goal '{instance.goal.name}'.",
            notification_type="info",
            user_action="milestone_creation"
        )
    elif instance.achieved:
        UserNotification.objects.create(
            user=instance.goal.account.user,
            account=instance.goal.account,
            title="Milestone Achieved",
            message=f"Congratulations! You have achieved the milestone of {instance.milestone_amount} for your goal '{instance.goal.name}'.",
            notification_type="success",
            user_action="milestone_achieved"
        )

@receiver(post_save, sender=SavingReminder)
def create_reminder_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.goal.account.user,
            account=instance.goal.account,
            title="Saving Reminder",
            message=f"Reminder: {instance.reminder_type} for your goal '{instance.goal.name}'.",
            notification_type="warning",
            user_action="saving_reminder"
        )

@receiver(post_save, sender=User)
def create_admin_notification(sender, instance, created, **kwargs):
    if created and instance.role == 'admin':
        AdminNotification.objects.create(
            user=instance,
            title="Admin Account Created",
            message="A new admin account has been created.",
            notification_type="info",
            admin_action="admin_account_creation"
        )

@receiver(post_save, sender=Investment)
def create_investment_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="New Investment Created",
            message=f"A new investment '{instance.investment_type.name}' has been created.",
            notification_type="info",
            user_action="investment_creation"
        )

@receiver(post_save, sender=UserInvestment)
def create_user_investment_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="User Investment Created",
            message=f"You have invested in '{instance.investment.investment_type.name}'.",
            notification_type="info",
            user_action="user_investment_creation"
        )

@receiver(post_save, sender=Dividend)
def create_dividend_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.investment_account.account.user,
            account=instance.investment_account.account,
            title="Dividend Distributed",
            message=f"A dividend of {instance.amount} has been distributed for your investment in '{instance.investment_type.name}'.",
            notification_type="success",
            user_action="dividend_distribution"
        )

@receiver(post_save, sender=Investment)
def update_investment_notification(sender, instance, created, **kwargs):
    if not created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="Investment Updated",
            message=f"Your investment '{instance.investment_type.name}' has been updated.",
            notification_type="info",
            user_action="investment_update"
        )

@receiver(post_save, sender=UserInvestment)
def update_user_investment_notification(sender, instance, created, **kwargs):
    if not created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="User Investment Updated",
            message=f"Your investment in '{instance.investment.investment_type.name}' has been updated.",
            notification_type="info",
            user_action="user_investment_update"
        )

@receiver(post_save, sender=Dividend)
def update_dividend_notification(sender, instance, created, **kwargs):
    if not created:
        UserNotification.objects.create(
            user=instance.investment_account.account.user,
            account=instance.investment_account.account,
            title="Dividend Updated",
            message=f"The dividend of {instance.amount} for your investment in '{instance.investment_type.name}' has been updated.",
            notification_type="info",
            user_action="dividend_update"
        )
@receiver(post_save, sender=Loan)
def create_loan_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="Loan Application Submitted",
            message=f"Your loan application for {instance.amount_requested} has been submitted.",
            notification_type="info",
            user_action="loan_application"
        )
    elif instance.status == "approved":
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="Loan Approved",
            message=f"Your loan application for {instance.amount_requested} has been approved.",
            notification_type="success",
            user_action="loan_approved"
        )
    elif instance.status == "rejected":
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="Loan Rejected",
            message=f"Your loan application for {instance.amount_requested} has been rejected.",
            notification_type="warning",
            user_action="loan_rejected"
        )

@receiver(post_save, sender=LoanPayment)
def create_loan_payment_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.loan.account.user,
            account=instance.loan.account,
            title="Loan Payment Made",
            message=f"A payment of {instance.amount} has been made for Loan #{instance.loan.id}.",
            notification_type="info",
            user_action="loan_payment"
        )

@receiver(post_save, sender=Loan)
def update_loan_notification(sender, instance, created, **kwargs):
    if not created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="Loan Updated",
            message=f"Your loan application for {instance.amount_requested} has been updated.",
            notification_type="info",
            user_action="loan_update"
        )

from savings.models import Goal, SavingMilestone, SavingReminder

@receiver(post_save, sender=Goal)
def create_goal_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="New Goal Created",
            message=f"A new goal '{instance.name}' has been created.",
            notification_type="info",
            user_action="goal_creation"
        )
    else:
        UserNotification.objects.create(
            user=instance.account.user,
            account=instance.account,
            title="Goal Updated",
            message=f"Your goal '{instance.name}' has been updated.",
            notification_type="info",
            user_action="goal_update"
        )

@receiver(post_save, sender=SavingMilestone)
def create_milestone_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.goal.account.user,
            account=instance.goal.account,
            title="Milestone Created",
            message=f"A new milestone of {instance.milestone_amount} has been set for your goal '{instance.goal.name}'.",
            notification_type="info",
            user_action="milestone_creation"
        )
    elif instance.achieved:
        UserNotification.objects.create(
            user=instance.goal.account.user,
            account=instance.goal.account,
            title="Milestone Achieved",
            message=f"Congratulations! You have achieved the milestone of {instance.milestone_amount} for your goal '{instance.goal.name}'.",
            notification_type="success",
            user_action="milestone_achieved"
        )

@receiver(post_save, sender=SavingReminder)
def create_reminder_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance.goal.account.user,
            account=instance.goal.account,
            title="Saving Reminder",
            message=f"Reminder: {instance.reminder_type} for your goal '{instance.goal.name}'.",
            notification_type="warning",
            user_action="saving_reminder"
        )
from userManager.models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_user_registration_notification(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(
            user=instance,
            title="User Registration",
            message=f"Welcome {instance.username}, your account has been successfully created.",
            notification_type="success",
            user_action="user_registration"
        )

@receiver(post_save, sender=CustomUser)
def update_user_profile_notification(sender, instance, created, **kwargs):
    if not created:
        UserNotification.objects.create(
            user=instance,
            title="Profile Updated",
            message=f"Your profile has been successfully updated.",
            notification_type="info",
            user_action="profile_update"
        )