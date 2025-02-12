import django_filters
from django.utils.timezone import now
from .models import Goal, Deposit, SavingMilestone, TransactionHistory

class GoalFilter(django_filters.FilterSet):
    min_progress = django_filters.NumberFilter(field_name="progress_percentage", lookup_expr="gte")
    max_progress = django_filters.NumberFilter(field_name="progress_percentage", lookup_expr="lte")
    min_deadline = django_filters.DateFilter(field_name="deadline", lookup_expr="gte")
    max_deadline = django_filters.DateFilter(field_name="deadline", lookup_expr="lte")
    account = django_filters.NumberFilter(field_name="account__id")
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Goal
        fields = ["account", "is_active", "min_progress", "max_progress", "min_deadline", "max_deadline"]


class DepositFilter(django_filters.FilterSet):
    goal = django_filters.NumberFilter(field_name="goal__id")
    min_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    max_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Deposit
        fields = ["goal", "min_date", "max_date", "min_amount", "max_amount"]


class SavingMilestoneFilter(django_filters.FilterSet):
    goal = django_filters.NumberFilter(field_name="goal__id")
    achieved = django_filters.BooleanFilter()

    class Meta:
        model = SavingMilestone
        fields = ["goal", "achieved"]


class TransactionHistoryFilter(django_filters.FilterSet):
    account = django_filters.NumberFilter(field_name="account__id")
    goal = django_filters.NumberFilter(field_name="goal__id")
    transaction_type = django_filters.CharFilter(field_name="transaction_type", lookup_expr="iexact")
    min_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    max_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = TransactionHistory
        fields = ["account", "goal", "transaction_type", "min_date", "max_date"]
