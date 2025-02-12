import django_filters
from .models import CustomUser

class UserFilter(django_filters.FilterSet):
    """
    Filter for CustomUser model.
    Allows filtering by email and role.
    """
    email = django_filters.CharFilter(lookup_expr='icontains')
    role = django_filters.ChoiceFilter(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['email', 'role']
