from rest_framework import serializers
from django.db import transaction
from .models import KYC, Account, NextOfKin
from userManager.serializers import CustomUserSerializer

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

    def validate_user(self, value):
        if self.instance:
            if KYC.objects.filter(user=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("KYC with this user already exists.")
        else:
            if KYC.objects.filter(user=value).exists():
                raise serializers.ValidationError("KYC with this user already exists.")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        next_of_kin_data = validated_data.pop('next_of_kin', [])
        existing_next_of_kin = {kin.id: kin for kin in instance.next_of_kin.all()}

        # Update or create next_of_kin
        for kin_data in next_of_kin_data:
            kin_id = kin_data.get('id')
            if kin_id and kin_id in existing_next_of_kin:
                kin_instance = existing_next_of_kin.pop(kin_id)
                for attr, value in kin_data.items():
                    setattr(kin_instance, attr, value)
                kin_instance.save()
            else:
                NextOfKin.objects.create(kyc=instance, **kin_data)

        # Delete removed next_of_kin
        for kin_to_delete in existing_next_of_kin.values():
            kin_to_delete.delete()

        # Update KYC fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class AccountSerializer(serializers.ModelSerializer):
    kyc = KYCSerializer(required=False, partial=True)
    user = CustomUserSerializer(required=False, partial=True)

    class Meta:
        model = Account
        fields = '__all__'

    @transaction.atomic
    def update(self, instance, validated_data):
        kyc_data = validated_data.pop('kyc', None)
        user_data = validated_data.pop('user', None)

        # Handle nested KYC updates
        if kyc_data:
            kyc_instance = getattr(instance, 'kyc', None)
            kyc_serializer = KYCSerializer(instance=kyc_instance, data=kyc_data, partial=True)
            kyc_serializer.is_valid(raise_exception=True)
            kyc_instance = kyc_serializer.save()
            instance.kyc = kyc_instance

        # Handle nested User updates
        if user_data:
            user_instance = getattr(instance, 'user', None)
            user_serializer = CustomUserSerializer(instance=user_instance, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_instance = user_serializer.save()
            instance.user = user_instance

        # Update Account fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
