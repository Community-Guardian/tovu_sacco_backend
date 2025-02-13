from django.contrib import admin
from .models import Notification, UserNotification, AdminNotification


class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'account', 'title', 'user_action', 'date_sent', 'is_read')
    list_filter = ('user_action', 'is_read', 'date_sent')
    search_fields = ('user__username', 'account__name', 'title', 'message')
    readonly_fields = ('date_sent',)

class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'admin_action', 'date_sent', 'is_read')
    list_filter = ('admin_action', 'is_read', 'date_sent')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('date_sent',)

admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(AdminNotification, AdminNotificationAdmin)