from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Initialize the DefaultRouter
router = DefaultRouter()

# Register ViewSets
router.register(r'goals', views.GoalViewSet, basename='goal')
router.register(r'deposits', views.DepositViewSet, basename='deposit')
router.register(r'milestones', views.SavingMilestoneViewSet, basename='milestone')
router.register(r'reminders', views.SavingReminderViewSet, basename='reminder')
router.register(r'transactions', views.TransactionHistoryViewSet, basename='transaction')
router.register(r'notifications', views.GoalNotificationViewSet, basename='notification')
router.register(r'goal-progress', views.GoalProgressUpdateView, basename='goal-progress')
router.register(r'make-deposit', views.MakeDepositViewSet, basename='make-deposit')

# URL patterns for the app
urlpatterns = [
    # Register the default router to auto-generate URLs for viewsets
    path('api/', include(router.urls)),
]
