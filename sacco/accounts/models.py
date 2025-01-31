from django.db import models
import uuid
from shortuuid.django_fields import ShortUUIDField
from django.db.models.signals import post_save
from django.dispatch import receiver 
# Create your models here.
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
import os

ACCOUNT_STATUS = (
    ("active", "Active"),
    ("pending", "Pending"),
    ("in-active", "In-active")
)

MARITAL_STATUS = (
    ("married", "Married"),
    ("single", "Single"),
    ("other", "Other")
)

GENDER = (
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other")
)


IDENTITY_TYPE = (
    ("national_id_card", "National ID Card"),
    ("drivers_licence", "Drives Licence"),
    ("international_passport", "International Passport")
)

EMPLOYMENT_STATUS = (
    ("unemployed", "Unemployed"),
    ("self_employed", "Self Employed"),
    ("employed", "Employed"),
    ("student", "Student"),
    ("retired", "Retired"),
    ("other", "Other")
)
def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{instance.user.id}_{uuid.uuid4()}.{ext}"
    return os.path.join('users/', filename)

class KYC(models.Model):
    membership_number = ShortUUIDField(
        length=10, unique=True, primary_key=True, max_length=20, 
        prefix="217", alphabet="abcdefghi1234567890", editable=False
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=1000)
    marital_status = models.CharField(choices=MARITAL_STATUS, max_length=40)
    gender = models.CharField(choices=GENDER, max_length=40)
    identity_type = models.CharField(choices=IDENTITY_TYPE, max_length=140)
    id_number = models.CharField(max_length=10, unique=True)
    identity_image = models.ImageField(upload_to=user_directory_path, default='res/default.png')
    date_of_birth = models.DateTimeField(auto_now_add=False)
    signature = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    kra_pin = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Address
    country = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact Detail
    contact_number = PhoneNumberField(unique=True)
    
    # KYC status
    kyc_submitted = models.BooleanField(default=False)
    kyc_confirmed = models.BooleanField(default=False)
    
    # Employment status
    employment_status = models.CharField(choices=EMPLOYMENT_STATUS, max_length=40, blank=True, null=True)

    def __str__(self):
        return f"{self.user}"  

    def save(self, *args, **kwargs):
        if not self.kyc_submitted:
            self.kyc_submitted = True
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class NextOfKin(models.Model):
    kyc = models.ForeignKey(KYC, on_delete=models.CASCADE, related_name="next_of_kin")
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)
    contact_number = PhoneNumberField()

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.kyc.user}"
class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kyc = models.OneToOneField(KYC, on_delete=models.DO_NOTHING, blank=True, null=True)
    account_balance = models.PositiveIntegerField(default=0)
    account_minimum_shares_balance = models.PositiveIntegerField(default=0)  # one time fee you pay for each account to become a full member
    account_number = ShortUUIDField(length=10,primary_key=True, editable=False,  unique=True,max_length= 25, prefix="ACC", alphabet="1234567890" )
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    is_full_member = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    recommended_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="recommended_by")

    class Meta:
        ordering = ['-last_modified']
        verbose_name = "Customer_Account"
        verbose_name_plural = "Customer_Accounts"

    def save(self, *args, **kwargs):
        # Ensure the KYC is linked to the account by default
        if not self.kyc_id:
            try:
                self.kyc = KYC.objects.get(user=self.user)
            except KYC.DoesNotExist:
                raise ValueError("KYC information is required before creating an account.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user}" 

    
