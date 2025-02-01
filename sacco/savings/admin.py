from django.contrib import admin
from .models import Goal, Deposit, SavingMilestone, SavingReminder, TransactionHistory, GoalNotification


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('account', 'name', 'target_amount', 'current_amount', 'progress_percentage', 'deadline', 'saving_frequency', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'account__user__username')
    list_filter = ('saving_frequency', 'deadline', 'is_active', 'created_at')
    list_editable = ('is_active',)
    fieldsets = (
        (None, {
            'fields': ('account', 'name', 'description', 'target_amount', 'current_amount', 'deadline', 'cover_icon', 'color', 'saving_frequency', 'is_active')
        }),
        ('Progress & Timing', {
            'fields': ('progress_percentage', 'created_at', 'updated_at')
        })
    )
    readonly_fields = ('progress_percentage', 'created_at', 'updated_at')


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ( 'goal', 'amount', 'date', 'transaction_id')
    search_fields = ('goal__name', 'account__user__username', 'transaction_id')
    list_filter = ('date', 'goal')
    readonly_fields = ('transaction_id', 'date')


@admin.register(SavingMilestone)
class SavingMilestoneAdmin(admin.ModelAdmin):
    list_display = ('goal', 'milestone_amount', 'milestone_date', 'achieved')
    search_fields = ('goal__name', 'milestone_amount')
    list_filter = ('achieved', 'milestone_date')
    list_editable = ('achieved',)


@admin.register(SavingReminder)
class SavingReminderAdmin(admin.ModelAdmin):
    list_display = ('goal', 'reminder_type', 'reminder_date', 'is_sent')
    search_fields = ('goal__name', 'reminder_type')
    list_filter = ('is_sent', 'reminder_date')
    list_editable = ('is_sent',)


@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('account', 'goal', 'amount', 'transaction_type', 'date', 'reference_number')
    search_fields = ('goal__name', 'account__user__username', 'reference_number')
    list_filter = ('transaction_type', 'date')
    readonly_fields = ('reference_number', 'date')


@admin.register(GoalNotification)
class GoalNotificationAdmin(admin.ModelAdmin):
    list_display = ('account', 'goal', 'notification_type', 'message', 'date_sent', 'is_read')
    search_fields = ('goal__name', 'account__user__username', 'notification_type')
    list_filter = ('is_read', 'date_sent')
    list_editable = ('is_read',)
