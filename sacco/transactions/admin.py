from django.conf import settings
from django.contrib import admin
from .models import (
    TransferTransaction,
    WithdrawTransaction,
    RefundTransaction,
    DepositTransaction,
)

class ReadOnlyAdmin(admin.ModelAdmin):
    """
    Base admin class to make transactions uneditable and undeletable after creation.
    """
    list_display = ('transaction_id', 'user', 'amount', 'status', 'date','is_processed')
    search_fields = ('transaction_id', 'user__username')
    actions = None  # Disable bulk actions

    def get_readonly_fields(self, request, obj=None):
        """
        Dynamically set readonly fields based on the model fields.
        """
        if settings.DEBUG:  # Enable adding in development or testing mode
            return []
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        """
        Allow adding new transactions only during testing.
        """
        if settings.DEBUG:  # Enable adding in development or testing mode
            return True
        return False

    def has_change_permission(self, request, obj=None):
        """
        Prevent editing transactions.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deleting transactions.
        """
        return False


@admin.register(TransferTransaction)
class TransferTransactionAdmin(ReadOnlyAdmin):
    model = TransferTransaction


# @admin.register(WithdrawTransaction)
# class WithdrawTransactionAdmin(ReadOnlyAdmin):
#     model = WithdrawTransaction


# @admin.register(RefundTransaction)
# class RefundTransactionAdmin(ReadOnlyAdmin):
#     model = RefundTransaction



@admin.register(DepositTransaction)
class DepositTransactionAdmin(ReadOnlyAdmin):
    model = DepositTransaction
