import logging
from django.db.models.signals import post_save,post_migrate
from django.dispatch import receiver
from django.db.models import Sum
from .models import Loan, UserLoanRequirement , LoanRequirement, LoanType,LoanPayment
from accounts.models import  Account
from django.utils.timezone import now, timedelta
import decimal
# Configure logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=LoanPayment)
def update_loan_status(sender, instance, **kwargs):
    """
    Update loan status based on payments made.
    """
    try:
        loan = instance.loan

        # Aggregate total payments made for the loan
        total_paid = loan.payments.aggregate(total=Sum("amount"))["total"] or 0

        logger.info(
            f"Loan #{loan.id}: Payment of {instance.amount} recorded. Total paid so far: {total_paid}."
        )

        # Check if the loan has been fully repaid
        if total_paid >= loan.amount_approved:
            loan.status = "repaid"
            loan.is_active = False
            logger.info(f"Loan #{loan.id} has been fully repaid. Marking it as inactive.")
        else:
            logger.info(f"Loan #{loan.id} still active. Outstanding amount: {loan.amount_approved - total_paid}.")

        # Save the updated loan status
        loan.save()

    except Exception as e:
        logger.error(
            f"Error updating loan status for Loan #{instance.loan.id}. Error: {str(e)}"
        )
@receiver(post_save, sender=Loan)
def create_user_requirements(sender, instance, created, **kwargs):
    """
    Generate UserLoanRequirement records based on LoanType requirements.
    """
    if created:
        loan_type = instance.loan_type
        account = instance.account

        for requirement in loan_type.requirements.all():
            UserLoanRequirement.objects.create(
                account=account,
                requirement=requirement,
                is_fulfilled=False
            )
        logger.info(f"Requirements generated for Loan #{instance.id} - {loan_type.name}")


@receiver(post_migrate)
def populate_sample_data(sender, **kwargs):
    """
    Populates sample loan requirements, loan types, and loans.
    """
    if sender.name != "loans": 
        return

    # Populate Loan Requirements
    try:
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

        # Populate Loan Types
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

    
    except Exception as e:
        print(f"Error populating sample data: {e}")