from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserNotificationViewSet, AdminNotificationViewSet

router = DefaultRouter()
router.register(r'user-notifications', UserNotificationViewSet, basename='user-notifications')
router.register(r'admin-notifications', AdminNotificationViewSet, basename='admin-notifications')

urlpatterns = [
    path('', include(router.urls)),
]