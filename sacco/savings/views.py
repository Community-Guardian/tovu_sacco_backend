from rest_framework import viewsets, permissions
from .models import Goal, Deposit, SavingMilestone, SavingReminder, TransactionHistory, GoalNotification
from .serializers import GoalSerializer, DepositSerializer, SavingMilestoneSerializer, SavingReminderSerializer, TransactionHistorySerializer, GoalNotificationSerializer, GoalProgressSerializer
from rest_framework.response import Response
from rest_framework import status , filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import GoalFilter, DepositFilter, SavingMilestoneFilter, TransactionHistoryFilter
# View for Goal (ModelViewSet)
class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GoalFilter
    search_fields = ['account', 'is_active', 'min_progress', 'max_progress', 'min_deadline', 'max_deadline']
    ordering_fields = ['account', 'is_active', 'min_progress', 'max_progress', 'min_deadline', 'max_deadline']
    ordering = ['-deadline']

    def get_queryset(self):
        # Only show goals for the authenticated user
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(account__user=user)
        return self.queryset  # Admin or any other role has access to all goals

    # def perform_create(self, serializer):
        # serializer.save(user=self.request.user)


# View for Deposit (ModelViewSet)
class DepositViewSet(viewsets.ModelViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DepositFilter
    search_fields = ['goal']
    ordering_fields = ['goal', 'date']
    ordering = ['-date']

    def get_queryset(self):
        # Only show deposits for the authenticated user's goals
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(goal__account__user=user)
        return self.queryset  # Admin or any other role has access to all deposits


# View for Saving Milestone (ModelViewSet)
class SavingMilestoneViewSet(viewsets.ModelViewSet):
    queryset = SavingMilestone.objects.all()
    serializer_class = SavingMilestoneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SavingMilestoneFilter
    search_fields = ['goal']
    ordering_fields = ['goal', 'milestone_date']
    ordering = ['-milestone_date']

    def get_queryset(self):
        # Only show milestones for the authenticated user's goals
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(goal__account__user=user)
        return self.queryset  # Admin or any other role has access to all milestones


# View for Saving Reminder (ModelViewSet)
class SavingReminderViewSet(viewsets.ModelViewSet):
    queryset = SavingReminder.objects.all()
    serializer_class = SavingReminderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['goal', 'reminder_date']
    ordering = ['-reminder_date']

    def get_queryset(self):
        # Only show reminders for the authenticated user's goals
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(goal__account__user=user)
        return self.queryset  # Admin or any other role has access to all reminders


# View for Transaction History (ModelViewSet)
class TransactionHistoryViewSet(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionHistoryFilter
    search_fields = ['account']
    ordering_fields = ['account', 'date']
    ordering = ['-date']

    def get_queryset(self):
        # Filter transaction history based on the authenticated user's goals
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(account__user=user)
        return self.queryset  # Admin or any other role has access to all transaction histories


# View for Goal Notifications (ModelViewSet)
class GoalNotificationViewSet(viewsets.ModelViewSet):
    queryset = GoalNotification.objects.all()
    serializer_class = GoalNotificationSerializer

    def get_queryset(self):
        # Return notifications related to the authenticated user
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(account__user=user)
        return self.queryset  # Admin or any other role has access to all notifications


# View to update the goal progress (Custom Update View)
class GoalProgressUpdateView(viewsets.ViewSet):
    queryset = GoalNotification.objects.all()
    serializer_class = GoalProgressSerializer

    permission_classes = [permissions.IsAuthenticated]
    

    def update(self, request, pk=None):
        try:
            goal = Goal.objects.get(id=pk, account__user=request.user)
        except Goal.DoesNotExist:
            return Response({'detail': 'Goal not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)

        # Assuming you pass the new amount in the request body
        current_amount = goal.current_amount
        new_deposit_amount = request.data.get('amount', 0)

        # Update goal progress
        goal.update_amount(new_deposit_amount)
        goal.progress_percentage = (goal.current_amount / goal.target_amount) * 100
        goal.save()

        return Response({'progress_percentage': goal.progress_percentage}, status=status.HTTP_200_OK)


# API to handle deposits related to specific goals (Custom view for deposits)
class MakeDepositViewSet(viewsets.ViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    def create(self, request, goal_id=None):
        try:
            print(goal_id)
            goal = Goal.objects.get(id=goal_id, account__user=request.user)
        except Goal.DoesNotExist:
            return Response({'detail': 'Goal not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            # Assign goal to the deposit and save
            serializer.save(user=request.user, goal=goal)
            goal.update_amount(serializer.validated_data['amount'])
            goal.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
