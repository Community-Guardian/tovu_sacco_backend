from django.contrib import admin
from .models import Account, KYC


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Account model.
    """
    list_display = ('user', 'account_number', 'account_balance', 'account_status', 'last_modified')
    list_filter = ('account_status', 'last_modified')
    search_fields = ('user__username', 'account_number', 'account_id', 'red_code')
    readonly_fields = ('id', 'account_number', 'account_id', 'pin_number', 'red_code', 'last_modified')
    ordering = ('-last_modified',)


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    """
    Admin configuration for the KYC model.
    """
    list_display = ('user', 'full_name', 'id_number', 'identity_type', 'kyc_submitted', 'kyc_confirmed', 'date')
    list_filter = ('kyc_submitted', 'kyc_confirmed', 'gender', 'marital_status', 'date')
    search_fields = ('user__username', 'full_name', 'id_number', 'kra_pin')
    readonly_fields = ('id', 'date')
    ordering = ('-date',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'full_name', 'date_of_birth', 'gender', 'marital_status', 'contact_number'),
        }),
        ('Identity Details', {
            'fields': ('identity_type', 'id_number', 'identity_image', 'signature', 'kra_pin'),
        }),
        ('Address', {
            'fields': ('country', 'state', 'city'),
        }),
        ('KYC Status', {
            'fields': ('kyc_submitted', 'kyc_confirmed'),
        }),
        ('Next of Kin', {
            'fields': ('next_of_kin_name', 'next_of_kin_relationship', 'next_of_kin_contact'),
        }),
        ('Accounts Linked', {
            'fields': ('account',),
        }),
    )
