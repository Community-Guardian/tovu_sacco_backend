from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification, UserNotification, AdminNotification
from .serializers import UserNotificationSerializer, AdminNotificationSerializer
from .filters import UserNotificationFilter, AdminNotificationFilter

class UserNotificationViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user-specific notifications.
    """
    queryset = UserNotification.objects.all()
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserNotificationFilter
    search_fields = ['title', 'message']
    ordering_fields = ['date_sent', 'title']
    ordering = ['-date_sent']

    def get_queryset(self):
        """
        This view should return a list of all the user-specific notifications
        for the currently authenticated user.
        """
        user = self.request.user
        return UserNotification.objects.filter(user=user)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Custom action to mark all notifications as read.
        """
        user = request.user
        UserNotification.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Custom action to mark a specific notification as read.
        """
        user = request.user
        try:
            notification = UserNotification.objects.get(pk=pk, user=user)
        except UserNotification.DoesNotExist:
            return Response({'status': 'notification not found'}, status=404)

        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

class AdminNotificationViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing admin-specific notifications.
    """
    queryset = AdminNotification.objects.all()
    serializer_class = AdminNotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AdminNotificationFilter
    search_fields = ['title', 'message']
    ordering_fields = ['date_sent', 'title']
    ordering = ['-date_sent']

    def get_queryset(self):
        """
        This view should return a list of all the admin-specific notifications
        for the currently authenticated admin user.
        """
        user = self.request.user
        return AdminNotification.objects.filter(user=user)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Custom action to mark all notifications as read.
        """
        user = request.user
        AdminNotification.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Custom action to mark a specific notification as read.
        """
        user = request.user
        notification = AdminNotification.objects.get(pk=pk)
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})