from django.contrib import admin
from .models import BaseTransaction, TransferTransaction, WithdrawTransaction, RefundTransaction, DepositTransaction, MinimumSharesDepositTransaction, AuditTransaction
from django.utils.html import format_html
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse  # Use reverse from django.urls


class AuditTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'field_name', 'old_value', 'new_value', 'updated_by', 'updated_at')
    search_fields = ('transaction__transaction_id', 'field_name', 'updated_by__username')
    list_filter = ('updated_at', 'updated_by')
    ordering = ('-updated_at',)

    def transaction(self, obj):
        # Displaying transaction information (ContentType and object_id)
        transaction = obj.transaction
        return format_html(
            '<a href="{}">{}</a>', 
            reverse('admin:%s_%s_change' % (transaction._meta.app_label, transaction._meta.model_name), 
                    args=[transaction.pk]),  # Use reverse instead of admin.reverse
            transaction.transaction_id
        )


class TransferTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'transaction_type', 'payment_method', 'date', 'sender_account', 'receiver_account')
    search_fields = ('transaction_id', 'user__username', 'receiver_account__user__username', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'transaction_type')
    ordering = ('-date',)


class WithdrawTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'account', 'amount', 'status', 'transaction_type', 'payment_method', 'date')
    search_fields = ('transaction_id', 'user__username', 'account__name', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'transaction_type')
    ordering = ('-date',)


class RefundTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'account', 'amount', 'status', 'transaction_type', 'payment_method', 'date')
    search_fields = ('transaction_id', 'user__username', 'account__name', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'transaction_type')
    ordering = ('-date',)


class DepositTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'account', 'amount', 'status', 'transaction_type', 'payment_method', 'date')
    search_fields = ('transaction_id', 'user__username', 'account__name', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'transaction_type')
    ordering = ('-date',)


class MinimumSharesDepositTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'account', 'amount', 'status', 'transaction_type', 'payment_method', 'date')
    search_fields = ('transaction_id', 'user__username', 'account__name', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'transaction_type')
    ordering = ('-date',)


# Registering models in admin
admin.site.register(AuditTransaction, AuditTransactionAdmin)
admin.site.register(TransferTransaction, TransferTransactionAdmin)
admin.site.register(WithdrawTransaction, WithdrawTransactionAdmin)
admin.site.register(RefundTransaction, RefundTransactionAdmin)
admin.site.register(DepositTransaction, DepositTransactionAdmin)
admin.site.register(MinimumSharesDepositTransaction, MinimumSharesDepositTransactionAdmin)