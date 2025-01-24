from django.db import models
from django.utils import timezone
from accounts.models import Account, KYC
from decimal import Decimal

# Investment Type Model
class InvestmentType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

# Investment Model
class Investment(models.Model):
    investment_type = models.ForeignKey(InvestmentType, on_delete=models.CASCADE, related_name="investments")
    amount_invested = models.DecimalField(max_digits=15, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    return_on_investment = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 12.5% return
    date_invested = models.DateTimeField(default=timezone.now)
    maturity_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.investment_type.name} Investment"

    @property
    def profit_or_loss(self):
        return self.current_value - self.amount_invested

    @property
    def roi_percentage(self):
        if self.amount_invested > 0:
            return ((self.current_value - self.amount_invested) / self.amount_invested) * 100
        return 0

# Investment Account Model
class InvestmentAccount(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    total_investments = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_profit_or_loss = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    last_updated = models.DateTimeField(auto_now=True)
    investment_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('10000.00'))  # Define limit here

    def __str__(self):
        return f"{self.account.user.username}'s Investment Account"  # Access user through account

    @property
    def investment_count(self):
        return self.user_investments.filter(investment__is_active=True).count()

    @property
    def active_investments_value(self):
        return self.user_investments.filter(investment__is_active=True).aggregate(
            total_value=models.Sum('investment__current_value')
        )['total_value'] or Decimal('0.00')

    @property
    def has_reached_investment_limit(self):
        total_invested = self.user_investments.filter(investment__is_active=True).aggregate(
            total_invested=models.Sum('invested_amount')
        )['total_invested'] or Decimal('0.00')
        return total_invested >= self.investment_limit

# User Investment Model
class UserInvestment(models.Model):
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE, related_name="user_investments")
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name="linked_user_investments")
    invested_amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Investment in {self.investment.investment_type.name} by {self.account.account.user.username}"

    @property
    def current_profit_or_loss(self):
        return self.investment.current_value - self.invested_amount

# Dividend Distribution Model
class Dividend(models.Model):
    investment_account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE, related_name="dividends")
    investment_type = models.ForeignKey(InvestmentType, on_delete=models.CASCADE, related_name="dividends")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_distributed = models.DateTimeField(default=timezone.now)
    is_distributed = models.BooleanField(default=False)

    def __str__(self):
        return f"Dividend for {self.investment_account.account.user.username} - {self.investment_type.name}"
    @property
    def calculate_dividend(self):
        # Calculate total investment value for the investment type
        total_investment_value = sum([
            user_investment.invested_amount for user_investment in UserInvestment.objects.filter(
                investment__investment_type=self.investment_type
            )
        ])
        
        # Check if total_investment_value is 0 to avoid division by zero
        if total_investment_value == Decimal('0.00'):
            return Decimal('0.00')  # Or handle it differently, as needed
        
        # Calculate user share if total investment value is not zero
        user_share = self.investment_account.total_investments / total_investment_value
        return self.amount * user_share
