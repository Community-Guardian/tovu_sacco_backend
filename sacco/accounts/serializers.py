from rest_framework import serializers
from django.db import transaction
from .models import KYC, Account, NextOfKin
from userManager.serializers import CustomUserSerializer

class NextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextOfKin
        fields = ['id', 'name', 'relationship', 'contact_number']


class KYCSerializer(serializers.ModelSerializer):
    next_of_kin = NextOfKinSerializer(many=True, required=False)

    class Meta:
        model = KYC
        fields = '__all__'

    def validate_id_number(self, value):
        if KYC.objects.filter(id_number=value).exclude(membership_number=self.instance.membership_number if self.instance else None).exists():
            raise serializers.ValidationError("This ID number is already in use.")
        return value

    def validate_kra_pin(self, value):
        if KYC.objects.filter(kra_pin=value).exclude(membership_number=self.instance.membership_number if self.instance else None).exists():
            raise serializers.ValidationError("This KRA PIN is already in use.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        next_of_kin_data = validated_data.pop('next_of_kin', [])
        kyc_instance = KYC.objects.create(**validated_data)

        # Create Next of Kin entries if provided
        for kin_data in next_of_kin_data:
            NextOfKin.objects.create(kyc=kyc_instance, **kin_data)

        return kyc_instance

    def update_next_of_kin(self, kyc_instance, next_of_kin_data):
        existing_kin_ids = [kin.get('id') for kin in next_of_kin_data if kin.get('id')]
        kyc_instance.next_of_kin.exclude(id__in=existing_kin_ids).delete()

        for kin_data in next_of_kin_data:
            kin_id = kin_data.get('id')
            if kin_id:
                NextOfKin.objects.filter(id=kin_id, kyc=kyc_instance).update(**kin_data)
            else:
                NextOfKin.objects.create(kyc=kyc_instance, **kin_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        next_of_kin_data = validated_data.pop('next_of_kin', [])
        self.update_next_of_kin(instance, next_of_kin_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def validate_user(self, value):
        query = KYC.objects.filter(user=value)
        if self.instance:
            query = query.exclude(user=self.instance.user)
        if query.exists():
            raise serializers.ValidationError("KYC with this user already exists.")
        return value

class AccountSerializer(serializers.ModelSerializer):
    kyc = KYCSerializer(required=False)
    user = CustomUserSerializer(required=False)

    class Meta:
        model = Account
        fields = '__all__'

    def update(self, instance, validated_data):
        print('creation')
        kyc_data = validated_data.pop('kyc', None)
        user_data = validated_data.pop('user', None)

        # Update or create KYC
        if kyc_data:
            if instance.kyc:

                KYCSerializer(instance.kyc, data=kyc_data, partial=True).is_valid(raise_exception=True)
                KYCSerializer(instance.kyc, data=kyc_data, partial=True).save()
            else:
                kyc_instance = KYCSerializer(data=kyc_data)
                kyc_instance.is_valid(raise_exception=True)
                instance.kyc = kyc_instance.save()

        # Update or create User
        if user_data:
            if instance.user:
                CustomUserSerializer(instance.user, data=user_data, partial=True).is_valid(raise_exception=True)
                CustomUserSerializer(instance.user, data=user_data, partial=True).save()
            else:
                user_instance = CustomUserSerializer(data=user_data)
                user_instance.is_valid(raise_exception=True)
                instance.user = user_instance.save()

        # Update Account fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
