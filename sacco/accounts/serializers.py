from rest_framework import serializers
from .models import KYC, Account,NextOfKin
from userManager.serializers import CustomUserSerializer
class NextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextOfKin
        fields = ['id', 'name', 'relationship', 'contact_number']


class KYCSerializer(serializers.ModelSerializer):
    next_of_kin = NextOfKinSerializer(many=True, read_only=True)  # Nested serializer

    class Meta:
        model = KYC
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    kyc = KYCSerializer()
    user = CustomUserSerializer()

    class Meta:
        model = Account
        fields = '__all__'
