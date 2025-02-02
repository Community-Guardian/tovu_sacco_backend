from rest_framework import serializers
from .models import KYC, Account,NextOfKin
from userManager.serializers import CustomUserSerializer
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
class NextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextOfKin
        fields = ['id', 'name', 'relationship', 'contact_number']


class KYCSerializer(serializers.ModelSerializer):
    next_of_kin = NextOfKinSerializer(many=True)

    class Meta:
        model = KYC
        fields = '__all__'
    def validate_id_number(self, value):
        if KYC.objects.filter(id_number=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("This ID number is already in use.")
        return value

    def validate_kra_pin(self, value):
        if KYC.objects.filter(kra_pin=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("This KRA PIN is already in use.")
        return value
    def update(self, instance, validated_data):
        # Handle next_of_kin updates
        next_of_kin_data = validated_data.pop('next_of_kin', [])

        # Update existing next_of_kin and add new ones
        existing_next_of_kin = {kin.id: kin for kin in instance.next_of_kin.all()}  # Assuming related_name='next_of_kin'

        for kin_data in next_of_kin_data:
            kin_id = kin_data.get('id', None)

            if kin_id and kin_id in existing_next_of_kin:
                # Update existing next_of_kin
                kin_instance = existing_next_of_kin.pop(kin_id)
                for attr, value in kin_data.items():
                    setattr(kin_instance, attr, value)
                kin_instance.save()
            else:
                # Create new next_of_kin
                NextOfKin.objects.create(kyc=instance, **kin_data)

        # Delete any next_of_kin not included in the update
        for kin_to_delete in existing_next_of_kin.values():
            kin_to_delete.delete()

        # Update KYC fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class AccountSerializer(serializers.ModelSerializer):
    kyc = KYCSerializer(required=False)
    user = CustomUserSerializer(required=False)

    class Meta:
        model = Account
        fields = '__all__'

    def update(self, instance, validated_data):
        kyc_data = validated_data.pop('kyc', None)
        user_data = validated_data.pop('user', None)

        # Handle KYC updates
        if kyc_data:
            kyc_instance = instance.kyc
            if kyc_instance:
                kyc_serializer = KYCSerializer(kyc_instance, data=kyc_data, partial=True)
                kyc_serializer.is_valid(raise_exception=True)
                kyc_serializer.save()
            else:
                # Create KYC if it doesn't exist
                kyc_serializer = KYCSerializer(data=kyc_data)
                kyc_serializer.is_valid(raise_exception=True)
                kyc_instance = kyc_serializer.save()
                instance.kyc = kyc_instance  # Associate with Account

        # Handle User updates
        if user_data:
            user_instance = instance.user
            if user_instance:
                user_serializer = CustomUserSerializer(user_instance, data=user_data, partial=True)
                user_serializer.is_valid(raise_exception=True)
                user_serializer.save()
            else:
                # Create User if it doesn't exist
                user_serializer = CustomUserSerializer(data=user_data)
                user_serializer.is_valid(raise_exception=True)
                user_instance = user_serializer.save()
                instance.user = user_instance  # Associate with Account

        # Update Account fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance