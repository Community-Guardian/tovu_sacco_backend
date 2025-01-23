from django.contrib import admin
from .models import LoanRequirement, UserLoanRequirement, LoanType, Loan, LoanPayment


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
        "interest_rate",
        "date_requested",
        "date_approved",
        "due_date",
        "status",
        "is_active",
    )
    list_filter = ("status", "is_active", "date_requested", "due_date")
    search_fields = ("account__user__username", "loan_type__name")
    ordering = ("-date_requested",)


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for LoanPayment.
    """
    list_display = ("loan", "amount", "payment_date")
    list_filter = ("payment_date",)
    search_fields = ("loan__id", "loan__account__user__username")
    ordering = ("-payment_date",)
