from rest_framework import serializers
from .models import Loan, LoanType, LoanRequirement, LoanPayment, UserLoanRequirement


class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = "__all__"


class LoanRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRequirement
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    requirements = LoanRequirementSerializer(many=True, read_only=True)
    loan_type = serializers.PrimaryKeyRelatedField(queryset=LoanType.objects.all())  # Accept loan_type ID

    class Meta:
        model = Loan
        fields = "__all__"
        read_only_fields = ["status", "date_requested", "date_approved"]

    def validate(self, data):
        # check if request is being mace by account owner
        if self.context["request"].user != data["account"].user:
            raise serializers.ValidationError("You are not authorized to make this request.")
        # Safely check if 'loan_type' exists in the data
        loan_type = data.get("loan_type")

        if loan_type is None:
            raise serializers.ValidationError("Loan type is required.")

        # Get the LoanType object using the provided ID
        loan_type_instance = LoanType.objects.get(id=loan_type.id)

        if data["amount_requested"] <= 0:
            raise serializers.ValidationError("The requested amount must be greater than 0.")

        if data["amount_requested"] > loan_type_instance.max_amount:
            raise serializers.ValidationError(f"The requested amount cannot exceed {loan_type_instance.max_amount}.")
        
        return data


class LoanPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanPayment
        fields = "__all__"


class UserLoanRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoanRequirement
        fields = "__all__"
        read_only_fields = ["id", "account", "requirement", "submitted_at"]

    def update(self, instance, validated_data):
        """
        Allow partial updates on specific fields like `is_fulfilled` or `document`.
        """
        instance.is_fulfilled = validated_data.get("is_fulfilled", instance.is_fulfilled)
        instance.document = validated_data.get("document", instance.document)
        instance.save()
        return instance
