from django.db import models
from django.utils import timezone
from accounts.models import Account
from datetime import timedelta
from decimal import Decimal

class Goal(models.Model):
    SAVING_FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('ONCE', 'Once-off'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deadline = models.DateField()
    cover_icon = models.ImageField(upload_to='goal_covers/', null=True, blank=True)
    color = models.CharField(max_length=7, default='#FFFFFF')  # Hex color for frontend personalization
    saving_frequency = models.CharField(max_length=8, choices=SAVING_FREQUENCY_CHOICES, default='MONTHLY')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)  # To track if goal is active
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def calculate_progress(self):
        if self.target_amount > 0:
            self.progress_percentage = (self.current_amount / self.target_amount) * 100
            self.save()

    def update_amount(self, deposit_amount):
        self.current_amount += deposit_amount
        self.calculate_progress()
        self.save()

    def generate_milestones(self):
        """Auto-create milestones based on target amount and frequency."""
        from .models import SavingMilestone  # Avoid circular import

        # Clear existing milestones (if goal is updated)
        self.milestones.all().delete()

        start_date = timezone.now().date()
        total_days = (self.deadline - start_date).days

        if total_days <= 0 or self.target_amount <= 0:
            return  # Avoid invalid milestone generation

        # Determine milestone intervals
        if self.saving_frequency == "DAILY":
            interval_days = 1
        elif self.saving_frequency == "WEEKLY":
            interval_days = 7
        elif self.saving_frequency == "MONTHLY":
            interval_days = 30
        else:
            interval_days = total_days  # 'ONCE' case

        num_intervals = total_days // interval_days
        milestone_amount_step = self.target_amount / Decimal(num_intervals) if num_intervals > 0 else self.target_amount

        milestones = []
        for i in range(1, num_intervals + 1):
            milestone_date = start_date + timedelta(days=i * interval_days)
            milestone_amount = milestone_amount_step * i
            milestones.append(SavingMilestone(goal=self, milestone_amount=milestone_amount, milestone_date=milestone_date))

        # Bulk create milestones
        SavingMilestone.objects.bulk_create(milestones)

    def save(self, *args, **kwargs):
        created = self.pk is None  # Check if it's a new goal
        super().save(*args, **kwargs)
        if created:
            self.generate_milestones()  # Auto-create milestones when a goal is first saved


class Deposit(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='deposits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # External transaction ID

    def __str__(self):
        return f"Deposit of {self.amount} to {self.goal.name}"

    class Meta:
        ordering = ['-date']


class SavingMilestone(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='milestones')
    milestone_amount = models.DecimalField(max_digits=12, decimal_places=2)
    milestone_date = models.DateField()
    achieved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Milestone of {self.milestone_amount} for {self.goal.name}"

    def mark_as_achieved(self):
        self.achieved = True
        self.save()


class SavingReminder(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=100)
    reminder_date = models.DateTimeField()
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.goal.name} on {self.reminder_date}"

    def mark_as_sent(self):
        self.is_sent = True
        self.save()


class TransactionHistory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transaction_history')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='transaction_history')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)  # E.g., Deposit, Withdrawal
    date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.goal.name} on {self.date}"


class GoalNotification(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=100)  # E.g., Progress, Milestone Reached
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.goal.name} - {self.notification_type}"
