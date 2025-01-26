from rest_framework import serializers
from .models import KYC, Account
from phonenumber_field.serializerfields import PhoneNumberField

class KYCSerializer(serializers.ModelSerializer):
    contact_number = PhoneNumberField()
    next_of_kin_contact = PhoneNumberField()

    class Meta:
        model = KYC
        fields = [
            'membership_number', 'user', 'full_name', 'marital_status', 'gender',
            'identity_type', 'id_number', 'identity_image', 'date_of_birth', 'signature',
            'kra_pin','employment_status', 'created_at', 'updated_at', 'country', 'county', 'town',
            'contact_number', 'kyc_submitted', 'kyc_confirmed',
            'next_of_kin_name', 'next_of_kin_relationship', 'next_of_kin_contact'
        ]

class AccountSerializer(serializers.ModelSerializer):
    kyc = KYCSerializer(read_only=True)

    class Meta:
        model = Account
        fields = [
            'user', 'kyc', 'account_balance', 'account_number', 'account_id',
            'created', 'is_active', 'is_suspended', 'last_modified', 'recommended_by'
        ]
