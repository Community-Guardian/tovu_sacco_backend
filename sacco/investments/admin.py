from django.contrib import admin
from .models import Investment

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Investment model. Adds list display and search functionality.
    This is for a single Sacco's investments.
    """
    list_display = ['id', 'name', 'amount_invested', 'roi_percentage', 'date_invested']
    search_fields = ['name', 'description']
