import django_filters
from django.utils.timezone import now
from .models import Loan, LoanPayment, LoanHistory

class LoanFilter(django_filters.FilterSet):
    account = django_filters.NumberFilter(field_name="account__id")
    loan_type = django_filters.NumberFilter(field_name="loan_type__id")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    min_amount_requested = django_filters.NumberFilter(field_name="amount_requested", lookup_expr="gte")
    max_amount_requested = django_filters.NumberFilter(field_name="amount_requested", lookup_expr="lte")
    min_date_requested = django_filters.DateFilter(field_name="date_requested", lookup_expr="gte")
    max_date_requested = django_filters.DateFilter(field_name="date_requested", lookup_expr="lte")
    due_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    due_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    
    class Meta:
        model = Loan
        fields = ["account", "loan_type", "status", "min_amount_requested", "max_amount_requested", "min_date_requested", "max_date_requested", "due_before", "due_after"]


class LoanPaymentFilter(django_filters.FilterSet):
    loan = django_filters.NumberFilter(field_name="loan__id")
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    min_payment_date = django_filters.DateFilter(field_name="payment_date", lookup_expr="gte")
    max_payment_date = django_filters.DateFilter(field_name="payment_date", lookup_expr="lte")

    class Meta:
        model = LoanPayment
        fields = ["loan", "min_amount", "max_amount", "min_payment_date", "max_payment_date"]


class LoanHistoryFilter(django_filters.FilterSet):
    loan = django_filters.NumberFilter(field_name="loan__id")
    change_type = django_filters.CharFilter(field_name="change_type", lookup_expr="iexact")
    changed_by = django_filters.NumberFilter(field_name="changed_by__id")
    min_timestamp = django_filters.DateFilter(field_name="timestamp", lookup_expr="gte")
    max_timestamp = django_filters.DateFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = LoanHistory
        fields = ["loan", "change_type", "changed_by", "min_timestamp", "max_timestamp"]
