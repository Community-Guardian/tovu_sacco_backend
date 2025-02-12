import django_filters
from .models import KYC, NextOfKin, Account

class KYCFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="user__username", lookup_expr="icontains")
    membership_number = django_filters.CharFilter(lookup_expr="iexact")
    id_number = django_filters.CharFilter(lookup_expr="iexact")
    kra_pin = django_filters.CharFilter(lookup_expr="iexact")
    marital_status = django_filters.ChoiceFilter(choices=KYC.MARITAL_STATUS)
    gender = django_filters.ChoiceFilter(choices=KYC.GENDER)
    country = django_filters.CharFilter(lookup_expr="icontains")
    county = django_filters.CharFilter(lookup_expr="icontains")
    kyc_submitted = django_filters.BooleanFilter()
    kyc_confirmed = django_filters.BooleanFilter()

    class Meta:
        model = KYC
        fields = ["membership_number", "id_number", "kra_pin", "marital_status", "gender", "kyc_submitted", "kyc_confirmed"]

class NextOfKinFilter(django_filters.FilterSet):
    kyc = django_filters.CharFilter(field_name="kyc__membership_number", lookup_expr="iexact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    relationship = django_filters.CharFilter(lookup_expr="icontains")
    contact_number = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = NextOfKin
        fields = ["kyc", "name", "relationship", "contact_number"]

class AccountFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="user__username", lookup_expr="icontains")
    account_number = django_filters.CharFilter(lookup_expr="iexact")
    is_active = django_filters.BooleanFilter()
    is_suspended = django_filters.BooleanFilter()
    is_full_member = django_filters.BooleanFilter()
    min_balance = django_filters.NumberFilter(field_name="account_balance", lookup_expr="gte")
    max_balance = django_filters.NumberFilter(field_name="account_balance", lookup_expr="lte")

    class Meta:
        model = Account
        fields = ["account_number", "user", "is_active", "is_suspended", "is_full_member"]
