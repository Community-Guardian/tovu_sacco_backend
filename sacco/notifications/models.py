from django.db import models
from django.utils import timezone
from accounts.models import Account
from django.contrib.auth import get_user_model

User = get_user_model()

NOTIFICATION_TYPES = (
    ('info', 'Info'),
    ('warning', 'Warning'),
    ('success', 'Success'),
)

class Notification(models.Model):
    """
    Base model for notifications.
    """
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='info')  # E.g., 'info', 'warning', 'success'
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.title}"

    class Meta:
        abstract = True
        ordering = ['-date_sent']

class UserNotification(Notification):
    """
    Model for user-specific notifications.
    """
    NOTIFICATION_TYPES = (
    ('info', 'Info'),
    ('warning', 'Warning'),
    ('success', 'Success'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications', limit_choices_to={'role': 'customer'})
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='user_notifications')
    user_action = models.CharField(max_length=100, blank=True, null=True)  # E.g., 'deposit', 'withdrawal'

    def __str__(self):
        return f"User Notification for {self.user.username} - {self.title}"

class AdminNotification(Notification):
    """
    Model for admin-specific notifications.
    """
    NOTIFICATION_TYPES = (
    ('info', 'Info'),
    ('warning', 'Warning'),
    ('success', 'Success'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_notifications', limit_choices_to={'role': 'admin'})
    admin_action = models.CharField(max_length=100, blank=True, null=True)  # E.g., 'user_registration', 'loan_approval'

    def __str__(self):
        return f"Admin Notification for {self.user.username} - {self.title}"