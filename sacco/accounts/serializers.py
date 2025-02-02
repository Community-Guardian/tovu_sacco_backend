from rest_framework import serializers
from .models import KYC, Account,NextOfKin
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
    kyc = KYCSerializer()
    user = CustomUserSerializer()

    class Meta:
        model = Account
        fields = '__all__'

    def update(self, instance, validated_data):
        # Handle KYC update
        kyc_data = validated_data.pop('kyc', None)
        if kyc_data:
            kyc_instance = instance.kyc
            for attr, value in kyc_data.items():
                setattr(kyc_instance, attr, value)
            kyc_instance.save()

        # Handle User update
        user_data = validated_data.pop('user', None)
        if user_data:
            user_instance = instance.user
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
            user_instance.save()

        # Handle Account update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance