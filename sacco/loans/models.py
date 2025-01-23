from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
from accounts.models import Account
from django.conf import settings
logger = logging.getLogger(__name__)

class LoanRequirement(models.Model):
    """
    Represents requirements for taking a loan.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_mandatory = models.BooleanField(default=True)  # Some requirements may be optional
    document_required = models.BooleanField(default=False)  # Indicate if a document needs to be uploaded
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
class UserLoanRequirement(models.Model):
    """
    Tracks a user's fulfillment of loan requirements.
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="user_requirements")
    requirement = models.ForeignKey(LoanRequirement, on_delete=models.CASCADE, related_name="user_requirements")
    is_fulfilled = models.BooleanField(default=False)
    document = models.FileField(upload_to="requirements/", blank=True, null=True)  # Optional document upload
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.account.user.username} - {self.requirement.name}"


class LoanType(models.Model):
    """
    Represents different types of loans.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage (e.g., 12.5%)
    requirements = models.ManyToManyField(LoanRequirement, related_name="loan_types")
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, default=1000.00)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00)
    max_duration_months = models.PositiveIntegerField(default=12)

    def __str__(self):
        return self.name




class Loan(models.Model):
    """
    Represents a loan taken by a user.
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="loans")
    loan_type = models.ForeignKey(LoanType, on_delete=models.PROTECT)
    amount_requested = models.DecimalField(max_digits=15, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    date_requested = models.DateTimeField(default=timezone.now)
    date_approved = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("repaid", "Repaid"),
        ],
        default="pending",
    )
    is_active = models.BooleanField(default=True)
    approvee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
    )

    def __str__(self):
        return f"Loan #{self.id} - {self.account.user.username}"

    def calculate_interest(self):
        """
        Calculate the total interest for the loan.
        """
        return self.amount_approved * (self.interest_rate / 100)

    def check_requirements(self):
        """
        Check if all mandatory requirements are fulfilled for this loan.
        """
        user_requirements = UserLoanRequirement.objects.filter(account=self.account, requirement__in=self.loan_type.requirements.all())
        unfulfilled_requirements = user_requirements.filter(is_fulfilled=False)

        if unfulfilled_requirements.exists():
            raise ValidationError(
                f"The following requirements are not fulfilled: {', '.join([req.requirement.name for req in unfulfilled_requirements])}"
            )
        return True

    def approve_loan(self):
        """
        Approve the loan after validating requirements.
        """
        try:
            self.check_requirements()
            self.status = "approved"
            self.date_approved = timezone.now()
            self.save()
            logger.info(f"Loan #{self.id} approved successfully.")
        except ValidationError as e:
            logger.error(f"Loan #{self.id} approval failed: {str(e)}")
            raise e
    def save(self, *args, **kwargs):
        """
        Automatically populate interest rate and date approved when the loan is approved.
        """
        # Set the interest rate based on the loan type if not already set
        if self.interest_rate is None and self.loan_type:
            self.interest_rate = self.loan_type.interest_rate

        if self.status == "approved":

            # Set the date approved if not already set
            if self.date_approved is None:
                self.date_approved = timezone.now()

        super().save(*args, **kwargs)
class LoanPayment(models.Model):
    """
    Tracks loan payments made by users.
    """
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment of {self.amount} for Loan #{self.loan.id}"
