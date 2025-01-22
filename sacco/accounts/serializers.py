import logging
from rest_framework import serializers
from .models import Account, KYC
from userManager.serializers import CustomUserSerializer
from django.core.exceptions import ValidationError
from django.db import transaction

# Configure logging
logger = logging.getLogger(__name__)

class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Account model.
    """
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['id', 'account_number', 'account_id', 'pin_number', 'red_code', 'date', 'user','account_balance']

    def create(self, validated_data):
        try:
            user = self.context['request'].user
            validated_data['user'] = user

            # Ensure the KYC is linked to the account by default
            if not validated_data.get('kyc'):
                try:
                    validated_data['kyc'] = KYC.objects.get(user=user)
                except KYC.DoesNotExist:
                    logger.error(f"KYC information is required for user {user.id} before creating an account.")
                    raise serializers.ValidationError("KYC information is required before creating an account. Please submit your KYC first.")

            account = super().create(validated_data)
            logger.info(f"Account created successfully for user {user.id} with account number {account.account_number}")
            return account
        except serializers.ValidationError as ve:
            logger.error(f"Validation error occurred while creating account: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating account for user {validated_data['user'].id}: {str(e)}")
            raise serializers.ValidationError(f"An error occurred while creating the account: {str(e)}")

    def update(self, instance, validated_data):
        try:
            user = self.context.get('request').user
            
            if not user.is_staff and not user.is_superuser:
                # Prevent modification of sensitive fields by non-admin users
                for field in ['user', 'account_number', 'account_id', 'pin_number', 'red_code']:
                    validated_data.pop(field, None)

            updated_instance = super().update(instance, validated_data)
            logger.info(f"Account updated successfully for user {user.id} with account number {instance.account_number}")
            return updated_instance
        except Exception as e:
            logger.error(f"Error occurred while updating account for user {instance.user.id}: {str(e)}")
            raise serializers.ValidationError(f"An error occurred while updating the account: {str(e)}")


class KYCSerializer(serializers.ModelSerializer):
    """
    Serializer for the KYC model.
    """
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = KYC
        fields = '__all__'
        read_only_fields = ['id', 'user', 'date', 'account']

    def create(self, validated_data):
        try:
            user = validated_data.get('user') or self.context.get('request').user
            
            # Use a transaction to prevent race conditions
            with transaction.atomic():
                if KYC.objects.filter(user=user).exists():
                    logger.warning(f"User {user.id} already has a KYC record.")
                    raise serializers.ValidationError({
                        "user": ["This user already has a KYC record."]
                    })
                validated_data['user'] = user
                kyc_instance = super().create(validated_data)
                logger.info(f"KYC record created successfully for user {user.id}.")
                return kyc_instance
        except serializers.ValidationError as ve:
            logger.error(f"Validation error occurred while creating KYC record for user {user.id}: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating KYC record for user {user.id}: {str(e)}")
            raise serializers.ValidationError(f"An error occurred while creating the KYC record: {str(e)}")

    def update(self, instance, validated_data):
        try:
            user = self.context.get('request').user

            if not user.is_staff and not user.is_superuser:
                # Prevent modification of specific fields by non-admin users
                restricted_fields = [
                    'kyc_submitted', 'kyc_confirmed', 'user', 'account', 
                    'identity_image', 'signature', 'kra_pin'
                ]
                for field in restricted_fields:
                    validated_data.pop(field, None)

            updated_instance = super().update(instance, validated_data)
            logger.info(f"KYC record updated successfully for user {user.id}.")
            return updated_instance
        except Exception as e:
            logger.error(f"Error occurred while updating KYC record for user {instance.user.id}: {str(e)}")
            raise serializers.ValidationError(f"An error occurred while updating the KYC record: {str(e)}")
