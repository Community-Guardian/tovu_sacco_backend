from django.contrib import admin
from .models import LoanRequirement, UserLoanRequirement, LoanType, Loan, LoanPayment, LoanHistory
from django.utils.timezone import now
from django.core.exceptions import ValidationError

@admin.register(LoanRequirement)
class LoanRequirementAdmin(admin.ModelAdmin):
    """
    Admin interface for LoanRequirement.
    """
    list_display = ("name", "is_mandatory", "document_required", "created_at", "updated_at")
    list_filter = ("is_mandatory", "document_required")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(UserLoanRequirement)
class UserLoanRequirementAdmin(admin.ModelAdmin):
    """
    Admin interface for UserLoanRequirement.
    """
    list_display = ("account", "requirement", "is_fulfilled", "submitted_at")
    list_filter = ("is_fulfilled",)
    search_fields = ("account__user__username", "requirement__name")
    ordering = ("-submitted_at",)


@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    """
    Admin interface for LoanType.
    """
    list_display = ("name", "interest_rate", "min_amount", "max_amount", "max_duration_months")
    search_fields = ("name",)
    filter_horizontal = ("requirements",)  # Enables selection of multiple requirements
    ordering = ("name",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """
    Admin interface for Loan.
    """
    list_display = (
        "id",
        "account",
        "loan_type",
        "amount_requested",
        "amount_approved",
        "amount_disbursed",
        "interest_rate",
        "date_requested",
        "date_approved",
        "date_disbursed",
        "due_date",
        "status",
        "is_active",
    )
    list_filter = ("status", "is_active", "date_requested", "due_date")
    search_fields = ("account__user__username", "loan_type__name")
    ordering = ("-date_requested",)
    actions = ["mark_as_disbursed"]

    def mark_as_disbursed(self, request, queryset):
        """
        Mark selected loans as disbursed if they are approved and not yet disbursed.
        """
        for loan in queryset.filter(status="approved", amount_disbursed__isnull=True):
            if not loan.amount_approved:
                raise ValidationError("Cannot disburse a loan with no approved amount.")

            loan.amount_disbursed = loan.amount_approved
            loan.date_disbursed = now()
            loan.save()

            # Log status change in LoanHistory
            LoanHistory.objects.create(
                loan=loan,
                changed_by=request.user,
                change_type="paid",
                notes="Loan fully disbursed",
            )

        self.message_user(request, "Selected loans marked as disbursed.")

    mark_as_disbursed.short_description = "Mark selected loans as disbursed"


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for LoanPayment.
    """
    list_display = ("loan", "amount", "payment_date")
    list_filter = ("payment_date",)
    search_fields = ("loan__id", "loan__account__user__username")
    ordering = ("-payment_date",)


@admin.register(LoanHistory)
class LoanHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for LoanHistory.
    """
    list_display = ("loan", "changed_by", "change_type", "timestamp", "notes")
    list_filter = ("change_type", "timestamp")
    search_fields = ("loan__id", "changed_by__username")
    ordering = ("-timestamp",)
