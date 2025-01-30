from django.utils import timezone  # Correct import for timezone.now()
from rest_framework import serializers
from .models import Goal, Deposit, SavingMilestone, SavingReminder, TransactionHistory, GoalNotification


# Serializer for the Goal model
class GoalSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Goal
        fields = '__all__'

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Target amount must be greater than zero.")
        return value

    def validate_deadline(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError("Deadline must be a future date.")
        return value

    def create(self, validated_data):
        # Assign the user to the goal before creating it
        # user = self.context['request'].user  # Get the user from the request context
        # validated_data['user'] = user  # Add the user to the validated data

        # Create and return the Goal instance
        return Goal.objects.create(**validated_data)

# Serializer for the Deposit model
class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = '__all__'

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Deposit amount must be greater than zero.")
        return value


# Serializer for the SavingMilestone model
class SavingMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingMilestone
        fields = '__all__'


# Serializer for the SavingReminder model
class SavingReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingReminder
        fields = '__all__'


# Serializer for the TransactionHistory model
class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = '__all__'


# Serializer for the GoalNotification model
class GoalNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalNotification
        fields = '__all__'


# Serializer to track the goal progress (especially for updates)
class GoalProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['current_amount', 'progress_percentage']

    def update(self, instance, validated_data):
        # Handle progress update logic, like calculating new progress_percentage
        instance.current_amount = validated_data.get('current_amount', instance.current_amount)
        instance.progress_percentage = (instance.current_amount / instance.target_amount) * 100
        instance.save()
        return instance
