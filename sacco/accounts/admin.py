from django.contrib import admin
from .models import Account, KYC


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'account_number', 'account_status', 'account_balance', 'kyc_submitted', 'kyc_confirmed', 'date']
    search_fields = ['user__username', 'account_number', 'red_code']
    list_filter = ['account_status', 'kyc_submitted', 'kyc_confirmed']
    readonly_fields = ['id', 'account_number', 'account_id', 'pin_number', 'red_code', 'date']


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'identity_type', 'date']
    search_fields = ['user__username', 'full_name', 'identity_type']
    list_filter = ['marital_status', 'gender', 'country']
    readonly_fields = ['id', 'date']
