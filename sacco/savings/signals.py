from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Goal, Deposit, SavingMilestone, SavingReminder, TransactionHistory, GoalNotification
from decimal import Decimal

# To track recursion prevention
def prevent_signal(instance):
    """Utility to prevent recursion when saving."""
    if hasattr(instance, '_prevent_signal'):
        return True
    instance._prevent_signal = True
    return False

# Signal to update goal progress when a new deposit is added
@receiver(post_save, sender=Deposit)
def update_goal_progress(sender, instance, created, **kwargs):
    if created and not prevent_signal(instance):
        # Update the goal's current amount and progress percentage
        goal = instance.goal
        goal.update_amount(instance.amount)

        # Ensure reference_number is unique
        reference_number = instance.transaction_id if instance.transaction_id else "N/A"

        # Check if a TransactionHistory entry with the same reference_number already exists
        # if not TransactionHistory.objects.filter(reference_number=reference_number).exists():
        # Create a new transaction history entry if it doesn't already exist
        TransactionHistory.objects.create(
            account=instance.goal.account,
            goal=goal,
            amount=instance.amount,
            transaction_type="Deposit",
            reference_number=reference_number
        )

        # Check if any milestone has been achieved
        milestones = SavingMilestone.objects.filter(goal=goal, milestone_amount__lte=goal.current_amount, achieved=False)
        for milestone in milestones:
            milestone.mark_as_achieved()

        # Optionally, create a notification about the deposit
        GoalNotification.objects.create(
            account=instance.goal.account,
            goal=goal,
            notification_type="Deposit Made",
            message=f"Your deposit of {instance.amount} has been successfully made. Current amount: {goal.current_amount}",
            date_sent=timezone.now(),
        )


# Signal to automatically send reminders based on the goal's saving frequency
@receiver(pre_save, sender=SavingReminder)
def set_reminder_date(sender, instance, **kwargs):
    # Set the reminder date based on the goal's saving frequency
    # if not instance.reminder_date:
        goal = instance.goal
        frequency = goal.saving_frequency

        # Determine the reminder date based on frequency
        if frequency == 'DAILY':
            instance.reminder_date = timezone.now() + timezone.timedelta(days=1)
        elif frequency == 'WEEKLY':
            instance.reminder_date = timezone.now() + timezone.timedelta(weeks=1)
        elif frequency == 'MONTHLY':
            instance.reminder_date = timezone.now() + timezone.timedelta(weeks=4)
        elif frequency == 'ONCE':
            instance.reminder_date = goal.deadline

# Signal to create a notification when a milestone is achieved
@receiver(post_save, sender=SavingMilestone)
def milestone_achieved(sender, instance, created, **kwargs):
    if created and instance.achieved and not prevent_signal(instance):
        # Create a notification for the user when a milestone is achieved
        goal = instance.goal
        GoalNotification.objects.create(
            account=goal.account,
            goal=goal,
            notification_type="Milestone Reached",
            message=f"Congratulations! You have reached a milestone of {instance.milestone_amount} for your goal '{goal.name}'.",
            date_sent=timezone.now(),
        )

# Signal to handle the creation of notifications when a goal is updated
@receiver(post_save, sender=Goal)
def goal_updated(sender, instance, created, **kwargs):
    if not created and not prevent_signal(instance):
        # Create a notification if a goal is updated (e.g., progress or deadline)
        GoalNotification.objects.create(
            account=instance.account,
            goal=instance,
            notification_type="Goal Updated",
            message=f"Your goal '{instance.name}' has been updated. Current amount: {instance.current_amount}, Progress: {instance.progress_percentage}%",
            date_sent=timezone.now(),
        )

# Signal to handle sending reminders to users
@receiver(post_save, sender=SavingReminder)
def send_saving_reminder(sender, instance, created, **kwargs):
    if created and not prevent_signal(instance):
        # Send reminder notifications when a saving reminder is created
        GoalNotification.objects.create(
            account=instance.goal.account,
            goal=instance.goal,
            notification_type="Saving Reminder",
            message=f"Reminder: It's time to save for your goal '{instance.goal.name}'. Don't forget to make a deposit!",
            date_sent=timezone.now(),
        )

# Signal to track deposit total progress and notify once goal is completed
@receiver(post_save, sender=Goal)
def check_goal_completion(sender, instance, created, **kwargs):
    if not created and instance.current_amount >= instance.target_amount and not prevent_signal(instance):
        # Goal has been completed
        GoalNotification.objects.create(
            account=instance.account,
            goal=instance,
            notification_type="Goal Completed",
            message=f"Congratulations! You have completed your goal '{instance.name}' with a total deposit of {instance.current_amount}.",
            date_sent=timezone.now(),
        )
        instance.is_active = False  # Deactivate the goal once it is completed
        instance.save()
