from rest_framework import serializers
from .models import Investment

class InvestmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Investment model to convert it into JSON format and validate data.
    """

    class Meta:
        model = Investment
        fields = ['id', 'name', 'description', 'amount_invested', 'date_invested', 'roi_percentage']
        read_only_fields = ['id', 'date_invested']  # ID and date_invested should not be editable
