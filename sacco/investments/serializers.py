# serializers.py
from rest_framework import serializers
from .models import InvestmentType, Investment, InvestmentAccount, UserInvestment, Dividend

class InvestmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentType
        fields = '__all__'

class InvestmentSerializer(serializers.ModelSerializer):
    investment_type = serializers.PrimaryKeyRelatedField(queryset=InvestmentType.objects.all())

    class Meta:
        model = Investment
        fields = '__all__'

class InvestmentAccountSerializer(serializers.ModelSerializer):
    total_investments = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit_or_loss = serializers.DecimalField(max_digits=15, decimal_places=2)
    investment_limit = serializers.DecimalField(max_digits=15, decimal_places=2)
    has_reached_investment_limit = serializers.BooleanField()

    class Meta:
        model = InvestmentAccount
        fields = '__all__'

class UserInvestmentSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField to allow creating a UserInvestment using the related model IDs
    account = serializers.PrimaryKeyRelatedField(queryset=InvestmentAccount.objects.all())
    investment = serializers.PrimaryKeyRelatedField(queryset=Investment.objects.all())
    class Meta:
        model = UserInvestment
        fields = '__all__'

class DividendSerializer(serializers.ModelSerializer):
    investment_account = InvestmentAccountSerializer()
    investment_type = InvestmentTypeSerializer()

    class Meta:
        model = Dividend
        fields = '__all__'
