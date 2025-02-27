from rest_framework import serializers
from .models import Loan, LoanType, LoanRequirement, LoanPayment, UserLoanRequirement,LoanHistory

class LoanRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRequirement
        fields = "__all__"
class LoanTypeSerializer(serializers.ModelSerializer):
    requirements_id = serializers.ListField(
        child=serializers.IntegerField(),  # Accepts a list of integers (IDs)
        write_only=True
    )
    requirements = LoanRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = LoanType
        fields = "__all__"

    def create(self, validated_data):
        # Extract the requirements_id from the validated data
        requirements_ids = validated_data.pop('requirements_id', [])

        # Create the LoanType instance
        loan_type = super().create(validated_data)

        # Associate the requirements with the LoanType instance
        if requirements_ids:
            requirements = LoanRequirement.objects.filter(id__in=requirements_ids)
            loan_type.requirements.set(requirements)  # Using a many-to-many relationship
            loan_type.save()

        return loan_type

    def update(self, instance, validated_data):
        # Extract the requirements_id from the validated data
        requirements_ids = validated_data.pop('requirements_id', [])

        # Update the LoanType instance
        instance = super().update(instance, validated_data)

        # Update or associate the requirements with the LoanType instance
        if requirements_ids:
            requirements = LoanRequirement.objects.filter(id__in=requirements_ids)
            instance.requirements.set(requirements)  # Using a many-to-many relationship
            instance.save()

        return instance
class LoanSerializer(serializers.ModelSerializer):
    requirements = LoanRequirementSerializer(many=True, read_only=True)
    loan_type = serializers.PrimaryKeyRelatedField(queryset=LoanType.objects.all())  # Accept loan_type ID

    class Meta:
        model = Loan
        fields = "__all__"
        read_only_fields = ["date_requested", "date_approved"]

    def validate(self, data):
        # check if request is being mace by account owner
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
class LoanHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField()  # Display username instead of user ID
    loan_id = serializers.IntegerField(source="loan.id", read_only=True)  # Include Loan ID

    class Meta:
        model = LoanHistory
        fields = ["id", "loan_id", "changed_by", "change_type", "timestamp", "notes"]