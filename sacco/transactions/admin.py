from django.contrib import admin
from .models import TransferTransaction, WithdrawTransaction, RefundTransaction, PaymentRequestTransaction, DepositTransaction

@admin.register(TransferTransaction)
class TransferTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'date')
    search_fields = ('transaction_id', 'user__username')

@admin.register(WithdrawTransaction)
class WithdrawTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'date')
    search_fields = ('transaction_id', 'user__username')

@admin.register(RefundTransaction)
class RefundTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'date')
    search_fields = ('transaction_id', 'user__username')

@admin.register(PaymentRequestTransaction)
class PaymentRequestTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'date')
    search_fields = ('transaction_id', 'user__username')

@admin.register(DepositTransaction)
class DepositTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'date')
    search_fields = ('transaction_id', 'user__username')