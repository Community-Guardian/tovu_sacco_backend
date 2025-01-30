from datetime import timezone
import logging
import threading
import decimal
from django.db.models.signals import post_save, pre_save, post_migrate
from django.dispatch import receiver
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta

from .models import Loan, UserLoanRequirement, LoanRequirement, LoanType, LoanPayment, LoanHistory
from accounts.models import Account

# Configure logging
logger = logging.getLogger(__name__)

# ✅ Thread-local storage to track recursion per request
thread_local = threading.local()

def is_recursing():
    """Check if the function is being called recursively within the same request."""
    if not hasattr(thread_local, "processing"):
        thread_local.processing = set()
    return thread_local.processing

def start_processing(key):
    """Mark a process as started to prevent recursion."""
    is_recursing().add(key)

def stop_processing(key):
    """Remove a process after it's completed."""
    is_recursing().discard(key)

# ✅ Loan Repayment & Status Updates
@receiver(post_save, sender=LoanPayment)
def update_loan_status(sender, instance, created, **kwargs):
    """
    Update loan status when a payment is made.
    Handles full repayments, overpayments, and status updates.
    """
    if not created:
        return  # Only act on new payments

    loan = instance.loan

    # Prevent recursive triggers
    key = f"update_loan_status_{loan.id}"
    if key in is_recursing():
        return
    start_processing(key)

    try:
        total_paid = loan.payments.aggregate(total=Sum("amount"))["total"] or decimal.Decimal("0.00")
        total_due = loan.amount_approved + loan.calculate_interest()

        logger.info(f"Loan #{loan.id}: Payment of {instance.amount} recorded. Total paid: {total_paid}, Total due: {total_due}.")

        if total_paid >= total_due:
            loan.status = "repaid"
            loan.is_active = False  # Mark loan as inactive
            logger.info(f"Loan #{loan.id} fully repaid. Status updated to 'repaid'.")
        else:
            logger.info(f"Loan #{loan.id} still active. Outstanding balance: {total_due - total_paid}.")

        loan.save()
    
    except Exception as e:
        logger.error(f"Error updating loan status for Loan #{loan.id}. Error: {str(e)}")
    
    finally:
        stop_processing(key)

# ✅ Validate Loan Before Approval
@receiver(pre_save, sender=Loan)
def validate_loan_before_approval(sender, instance, **kwargs):
    """
    Ensure all requirements are met before approving a loan.
    """
    if instance.status == "approved":
        try:
            instance.check_requirements()
            logger.info(f"Loan #{instance.id} requirements validated successfully.")
        except ValidationError as e:
            logger.error(f"Loan #{instance.id} cannot be approved: {str(e)}")
            raise e  # Prevent loan from being saved if requirements aren't met

# ✅ Generate User Loan Requirements on Loan Creation
@receiver(post_save, sender=Loan)
def create_user_requirements(sender, instance, created, **kwargs):
    """
    Automatically create UserLoanRequirement records when a loan is created.
    """
    if created:
        key = f"user_requirements_{instance.id}"
        if key in is_recursing():
            return
        start_processing(key)

        try:
            for requirement in instance.loan_type.requirements.all():
                UserLoanRequirement.objects.get_or_create(
                    account=instance.account,
                    requirement=requirement,
                    defaults={"is_fulfilled": False}
                )
            logger.info(f"Requirements generated for Loan #{instance.id}.")
        except Exception as e:
            logger.error(f"Error creating requirements for Loan #{instance.id}: {e}")
        finally:
            stop_processing(key)

# ✅ Automatically Set Due Date and Interest Rate
@receiver(pre_save, sender=Loan)
def set_loan_defaults(sender, instance, **kwargs):
    """
    Ensure loan has a due date and interest rate set correctly before saving.
    """
    if not instance.interest_rate:
        instance.interest_rate = instance.loan_type.interest_rate

    if instance.status == "approved" and not instance.date_approved:
        instance.date_approved = now()

    if not instance.due_date:
        instance.due_date = now().date() + timedelta(days=instance.loan_type.max_duration_months * 30)

# ✅ Sample Data Population (Runs After Migrations)
@receiver(post_migrate)
def populate_sample_data(sender, **kwargs):
    """
    Populates sample loan requirements, loan types, and loans.
    """
    if sender.name != "loans":
        return

    try:
        logger.info("Populating sample loan data...")

        # Loan Requirements
        req1, _ = LoanRequirement.objects.get_or_create(
            name="Proof of Income",
            defaults={"description": "Recent pay slips or bank statements", "is_mandatory": True, "document_required": True}
        )
        req2, _ = LoanRequirement.objects.get_or_create(
            name="Identification Document",
            defaults={"description": "Government-issued ID or passport", "is_mandatory": True, "document_required": True}
        )
        req3, _ = LoanRequirement.objects.get_or_create(
            name="Guarantor",
            defaults={"description": "Guarantor details for loan approval", "is_mandatory": False, "document_required": False}
        )

        # Loan Types
        loan_type1, _ = LoanType.objects.get_or_create(
            name="Personal Loan",
            defaults={
                "description": "A loan for personal use.",
                "interest_rate": decimal.Decimal("12.5"),
                "min_amount": decimal.Decimal("5000.00"),
                "max_amount": decimal.Decimal("100000.00"),
                "max_duration_months": 24,
            },
        )
        loan_type2, _ = LoanType.objects.get_or_create(
            name="Business Loan",
            defaults={
                "description": "A loan for business investments.",
                "interest_rate": decimal.Decimal("15.0"),
                "min_amount": decimal.Decimal("20000.00"),
                "max_amount": decimal.Decimal("500000.00"),
                "max_duration_months": 36,
            },
        )

        # Associate requirements with loan types
        loan_type1.requirements.add(req1, req2)
        loan_type2.requirements.add(req1, req2, req3)

        logger.info("Sample data population completed.")

    except Exception as e:
        logger.error(f"Error populating sample data: {e}")
@receiver(post_save, sender=UserLoanRequirement)
def check_fulfilled_requirements(sender, instance, **kwargs):
    """
    Automatically approve loan if all requirements are met.
    """
    loan = Loan.objects.filter(account=instance.account, status="pending").first()
    if loan and loan.check_requirements():
        loan.status = "approved"
        loan.date_approved = timezone.now()
        loan.save()
@receiver(post_save, sender=Loan)
def log_loan_status_change(sender, instance, created, **kwargs):
    """
    Create a LoanHistory record when a loan is approved or rejected.
    """
    if not created:  # Ensure it's an update, not a new loan creation
        if instance.status in ["approved", "rejected"]:
            LoanHistory.objects.create(
                loan=instance,
                changed_by=instance.approvee,
                change_type=instance.status,
                notes=f"Loan marked as {instance.status}.",
            )
            logger.info(f"Loan #{instance.id} marked as {instance.status}.")

@receiver(post_save, sender=LoanPayment)
def log_loan_payment(sender, instance, **kwargs):
    """
    Create a LoanHistory record when a payment is made.
    """
    LoanHistory.objects.create(
        loan=instance.loan,
        changed_by=instance.loan.account.user,  # Payment is made by the loan holder
        change_type="paid",
        notes=f"Payment of {instance.amount} made on {now().strftime('%Y-%m-%d')}.",
    )
    logger.info(f"Loan #{instance.loan.id} received a payment of {instance.amount}.")