# admin.py
from django.contrib import admin
from django.db.models import Sum
from .models import InvestmentType, Investment, InvestmentAccount, UserInvestment, Dividend

# Investment Type Model Admin
class InvestmentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name', 'description']

# Investment Model Admin
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'investment_type', 'amount_invested', 'current_value', 'return_on_investment', 'date_invested', 'maturity_date', 'is_active']
    list_filter = ['investment_type', 'is_active']
    search_fields = ['investment_type__name', 'description']

# Investment Account Model Admin
class InvestmentAccountAdmin(admin.ModelAdmin):
    list_display = ['account', 'total_investments', 'total_profit_or_loss', 'last_updated', 'investment_limit', 'investment_count', 'active_investments_value', 'has_reached_investment_limit']
    search_fields = ['account__user__username']
    readonly_fields = ['total_investments', 'total_profit_or_loss', 'last_updated', 'investment_count', 'active_investments_value', 'has_reached_investment_limit']

    def investment_count(self, obj):
        return obj.investment_count
    investment_count.admin_order_field = 'investment_count'  # Allows ordering by investment_count

    def active_investments_value(self, obj):
        return obj.active_investments_value
    active_investments_value.admin_order_field = 'active_investments_value'  # Allows ordering by active_investments_value

    def has_reached_investment_limit(self, obj):
        return obj.has_reached_investment_limit
    has_reached_investment_limit.admin_order_field = 'has_reached_investment_limit'  # Allows ordering by has_reached_investment_limit

# User Investment Model Admin
class UserInvestmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'investment', 'invested_amount', 'date_added', 'current_profit_or_loss']
    list_filter = ['account', 'investment']
    search_fields = ['account__user__username', 'investment__investment_type__name']

# Dividend Model Admin
class DividendAdmin(admin.ModelAdmin):
    list_display = ['id', 'investment_account', 'investment_type', 'amount', 'date_distributed', 'is_distributed', 'calculate_dividend']
    list_filter = ['investment_account', 'investment_type', 'is_distributed']
    search_fields = ['investment_account__account__user__username', 'investment_type__name']

    def calculate_dividend(self, obj):
        # Custom calculation for dividends
        return obj.calculate_dividend
    calculate_dividend.admin_order_field = 'calculate_dividend'  # Allows ordering by calculated dividend

# Register the models with the custom admin classes
admin.site.register(InvestmentType, InvestmentTypeAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(InvestmentAccount, InvestmentAccountAdmin)
admin.site.register(UserInvestment, UserInvestmentAdmin)
admin.site.register(Dividend, DividendAdmin)
