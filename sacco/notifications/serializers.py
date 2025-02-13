from rest_framework import serializers
from .models import  UserNotification, AdminNotification

class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['id', 'user', 'account', 'title', 'message', 'notification_type', 'user_action', 'date_sent', 'is_read']

class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 'admin_action', 'date_sent', 'is_read']