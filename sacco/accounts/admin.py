from django.contrib import admin
from .models import KYC, Account, NextOfKin
from shortuuid.django_fields import ShortUUIDField


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'identity_type', 'id_number', 'kyc_submitted', 'kyc_confirmed', 'created_at']
    search_fields = ['user__username', 'full_name', 'id_number']
    list_filter = ['kyc_submitted', 'kyc_confirmed', 'created_at']
    readonly_fields = ['membership_number', 'created_at', 'updated_at']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_number', 'account_balance', 'is_active', 'is_suspended', 'created']
    search_fields = ['user__username', 'account_number']
    list_filter = ['is_active', 'is_suspended', 'created']
    readonly_fields = ['account_number', 'account_minimum_shares_balance', 'account_balance', 'created', 'last_modified']


@admin.register(NextOfKin)
class NextOfKinAdmin(admin.ModelAdmin):
    list_display = ['kyc', 'name', 'relationship', 'contact_number']
    search_fields = ['name', 'relationship', 'contact_number', 'kyc__user__username']
    list_filter = ['relationship']
