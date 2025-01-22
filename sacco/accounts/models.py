from django.db import models
import uuid
from shortuuid.django_fields import ShortUUIDField
from django.db.models.signals import post_save
from django.dispatch import receiver 
# Create your models here.
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

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


def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s_%s" % (instance.id, ext)
    return "user_{0}/{1}".format(instance.user.id, filename)



class Account(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    account_number = ShortUUIDField(length=10, unique=True,max_length= 25, prefix="217", alphabet="1234567890" )
    account_id = ShortUUIDField(length=7, unique=True,max_length= 25, prefix="DEX", alphabet="1234567890" )
    pin_number = ShortUUIDField(length=4, unique=True,max_length= 7 , alphabet="1234567890" )
    red_code = ShortUUIDField(length=10, unique=True,max_length= 20, prefix="217", alphabet="abcdefghi1234567890" )
    account_status = models.CharField(max_length=100, choices= ACCOUNT_STATUS, default="in-active")
    date = models.DateTimeField(auto_now_add=True)
    kyc_submitted = models.BooleanField(default=False)
    kyc_confirmed = models.BooleanField(default=False)
    recommended_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="recommended_by")

    class Meta:
        ordering = ['-date']


    def __str__(self):
        return f"{self.user}" 
class KYC(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user =  models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account =  models.OneToOneField(Account, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=1000)
    image = models.ImageField(default="default.jpg" ,upload_to=user_directory_path)
    marital_status = models.CharField(choices=MARITAL_STATUS, max_length=40)
    gender = models.CharField(choices=GENDER, max_length=40)
    identity_type = models.CharField(choices=IDENTITY_TYPE, max_length=140)
    id_number = models.CharField(max_length=10)
    identity_image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    date_of_birth = models.DateTimeField(auto_now_add=False)
    signature = models.ImageField(upload_to=user_directory_path)

    # Address
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    # Contact Detail
    contact_number = PhoneNumberField(blank=True, null=True, unique=True)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user}"    

    
    class Meta:
        ordering = ['-date']