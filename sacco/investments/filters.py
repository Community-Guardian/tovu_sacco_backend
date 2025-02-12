import django_filters
from .models import Investment, InvestmentType, UserInvestment, InvestmentAccount, Dividend
from django.db import models

class InvestmentFilter(django_filters.FilterSet):
    investment_type = django_filters.ModelChoiceFilter(queryset=InvestmentType.objects.all())
    min_amount = django_filters.NumberFilter(field_name="amount_invested", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount_invested", lookup_expr="lte")
    min_return = django_filters.NumberFilter(field_name="return_on_investment", lookup_expr="gte")
    max_return = django_filters.NumberFilter(field_name="return_on_investment", lookup_expr="lte")
    is_active = django_filters.BooleanFilter()
    maturity_date_before = django_filters.DateFilter(field_name="maturity_date", lookup_expr="lte")
    maturity_date_after = django_filters.DateFilter(field_name="maturity_date", lookup_expr="gte")

    class Meta:
        model = Investment
        fields = ["investment_type", "is_active", "maturity_date"]

class UserInvestmentFilter(django_filters.FilterSet):
    account = django_filters.NumberFilter(field_name="account__id")
    investment = django_filters.NumberFilter(field_name="investment__id")
    min_amount = django_filters.NumberFilter(field_name="invested_amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="invested_amount", lookup_expr="lte")
    date_added_after = django_filters.DateFilter(field_name="date_added", lookup_expr="gte")
    date_added_before = django_filters.DateFilter(field_name="date_added", lookup_expr="lte")

    class Meta:
        model = UserInvestment
        fields = ["account", "investment"]

class InvestmentAccountFilter(django_filters.FilterSet):
    account = django_filters.NumberFilter(field_name="account__id")
    min_total_investments = django_filters.NumberFilter(field_name="total_investments", lookup_expr="gte")
    max_total_investments = django_filters.NumberFilter(field_name="total_investments", lookup_expr="lte")
    has_reached_limit = django_filters.BooleanFilter(method="filter_has_reached_limit")

    def filter_has_reached_limit(self, queryset, name, value):
        return queryset.filter(total_investments__gte=models.F("investment_limit")) if value else queryset

    class Meta:
        model = InvestmentAccount
        fields = ["account"]

class DividendFilter(django_filters.FilterSet):
    investment_type = django_filters.ModelChoiceFilter(queryset=InvestmentType.objects.all())
    investment_account = django_filters.NumberFilter(field_name="investment_account__id")
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    date_distributed_after = django_filters.DateFilter(field_name="date_distributed", lookup_expr="gte")
    date_distributed_before = django_filters.DateFilter(field_name="date_distributed", lookup_expr="lte")
    is_distributed = django_filters.BooleanFilter()

    class Meta:
        model = Dividend
        fields = ["investment_type", "investment_account", "is_distributed"]
