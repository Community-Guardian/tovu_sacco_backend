from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from phonenumber_field.modelfields import PhoneNumberField


def user_profile_image_path(instance, filename):
    """
    Generate a unique file path for user profile images.
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_{uuid.uuid4()}.{ext}"
    return f'users/{filename}'


class CustomUser(AbstractUser):
    """
    Custom user model with extended fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(null=True, blank=True, upload_to=user_profile_image_path)
    contact_number = PhoneNumberField(blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')
    # Override groups and permissions with unique related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Use unique related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Use unique related_name
        blank=True
    )

    def __str__(self):
        return self.username
