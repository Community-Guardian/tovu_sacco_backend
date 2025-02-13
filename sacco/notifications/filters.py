import django_filters
from .models import UserNotification, AdminNotification

class UserNotificationFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    notification_type = django_filters.ChoiceFilter(choices=UserNotification.NOTIFICATION_TYPES)
    date_sent = django_filters.DateFromToRangeFilter()

    class Meta:
        model = UserNotification
        fields = ['title', 'notification_type', 'date_sent', 'is_read']

class AdminNotificationFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    notification_type = django_filters.ChoiceFilter(choices=AdminNotification.NOTIFICATION_TYPES)
    date_sent = django_filters.DateFromToRangeFilter()

    class Meta:
        model = AdminNotification
        fields = ['title', 'notification_type', 'date_sent', 'is_read']