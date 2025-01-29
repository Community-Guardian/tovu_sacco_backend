from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import InvestmentType
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import InvestmentAccount, Dividend, InvestmentType, UserInvestment,Investment
from accounts.models import Account
from decimal import Decimal
from django.db import models
from django.db import transaction

# Signal to create InvestmentAccount and Dividends when Account is created
@receiver(post_save, sender=Account)
def create_investment_account(sender, instance, created, **kwargs):
    if created:
        # Create the InvestmentAccount for the user
        investment_account = InvestmentAccount.objects.create(account=instance)
        
        # Fetch all investment types and create dividends for each type
        for investment_type in InvestmentType.objects.all():
            # Initialize dividend for each investment type
            Dividend.objects.create(
                investment_account=investment_account,
                investment_type=investment_type,
                amount=Decimal('0.00'),
                is_distributed=False
            )
            
        print(f"Investment Account and Dividends created for {instance.user.username}")

# Signal to update the dividends based on the investments
@receiver(post_save, sender=UserInvestment)
def update_dividend_distribution(sender, instance, created, **kwargs):
    if created or instance.invested_amount != instance._meta.get_field('invested_amount').get_default():
        # Fetch the corresponding Dividend instance for the investment type
        dividend = Dividend.objects.filter(
            investment_account=instance.account,
            investment_type=instance.investment.investment_type
        ).first()

        if dividend:
            # Ensure the dividend instance has all necessary data before calculating the dividend
            if dividend.investment_account and dividend.investment_type:
                dividend_amount = dividend.calculate_dividend  # This property will be safe to use
                dividend.amount = dividend_amount
                dividend.save()

                # Access user through the related account
                user = instance.account.account.user
                print(f"Dividend updated for {user.username}")
            else:
                print(f"Dividend not updated for {instance.account.user.username} due to missing data.")
        else:
            print(f"No dividend found for {instance.account.user.username}.")
@receiver(post_migrate)
def create_sample_investment_types(sender, **kwargs):
    """
    Signal to create sample InvestmentType records after migration.
    """
    if sender.name == "investments":  # Replace 'investments' with your app name
        sample_data = [
            {"name": "Real Estate", "description": "Investments in real estate properties."},
            {"name": "Stock Market", "description": "Investments in stock market portfolios."},
            {"name": "Cryptocurrency", "description": "Investments in cryptocurrencies and tokens."},
            {"name": "Bonds", "description": "Investments in government and corporate bonds."},
            {"name": "Mutual Funds", "description": "Investments in professionally managed portfolios."},
        ]

        for data in sample_data:
            InvestmentType.objects.get_or_create(name=data["name"], defaults={"description": data["description"]})
# Ensure total investment balance is updated after an investment is added or updated
@receiver(post_save, sender=UserInvestment)
def update_investment_account_balance(sender, instance, created, **kwargs):
    """
    This signal will update the InvestmentAccount's total investment and profit/loss
    after a new UserInvestment is created or updated.
    """
    investment_account = instance.account
    investment = instance.investment
    
    # Recalculate the total investments for the account
    total_investments = investment_account.user_investments.filter(investment__is_active=True).aggregate(
        total=models.Sum('invested_amount')
    )['total'] or Decimal('0.00')
    
    # Update the total_investments and total_profit_or_loss
    total_profit_or_loss = sum(
        [user_investment.investment.profit_or_loss for user_investment in investment_account.user_investments.all()]
    )
    
    # Update the investment account totals in a transaction to avoid partial updates
    with transaction.atomic():
        investment_account.total_investments = total_investments
        investment_account.total_profit_or_loss = total_profit_or_loss
        investment_account.save()

# Ensure that the total profit or loss is recalculated when an investment is updated
@receiver(post_save, sender=Investment)
def update_investment_profit_loss(sender, instance, created, **kwargs):
    """
    This signal recalculates the profit or loss of the user's investments
    whenever the 'current_value' or other investment parameters change.
    """
    for user_investment in UserInvestment.objects.filter(investment=instance):
        # Recalculate the profit/loss for each user investment
        user_investment.account.total_profit_or_loss = sum(
            [user_investment.investment.profit_or_loss for user_investment in user_investment.account.user_investments.all()]
        )
        user_investment.account.save()

# Automatically update total investments and profit/loss in the InvestmentAccount after Dividend distribution
@receiver(post_save, sender=Dividend)
def update_investment_account_after_dividend(sender, instance, created, **kwargs):
    """
    This signal will update the InvestmentAccount's total investments and profit/loss
    when a dividend is distributed.
    """
    if instance.is_distributed:
        # Update total profit or loss after dividend distribution
        for user_investment in instance.investment_account.user_investments.all():
            user_investment.account.total_profit_or_loss = sum(
                [user_investment.investment.profit_or_loss for user_investment in user_investment.account.user_investments.all()]
            )
            user_investment.account.save()

# Ensure that the investment limit is checked before saving a new investment
@receiver(pre_save, sender=UserInvestment)
def check_investment_limit(sender, instance, **kwargs):
    """
    This signal ensures that a user's investment does not exceed their investment limit
    before it is saved.
    """
    investment_account = instance.account
    total_invested = investment_account.user_investments.filter(investment__is_active=True).aggregate(
        total=models.Sum('invested_amount')
    )['total'] or Decimal('0.00')
    
    new_total_investment = total_invested + instance.invested_amount
    if new_total_investment > investment_account.investment_limit:
        raise ValueError(f"Investment exceeds the allowed limit of {investment_account.investment_limit}")
# Signal to update the total amount invested for a specific investment when a user invests
@receiver(post_save, sender=UserInvestment)
def update_investment_total(sender, instance, created, **kwargs):
    """
    This signal will update the total amount invested for the specific investment
    when a user makes an investment.
    """
    if created:
        investment = instance.investment
        # Sum up all the invested amounts for this specific investment
        total_invested = sum([
            user_investment.invested_amount for user_investment in investment.linked_user_investments.all()
        ])

        # Update the total amount invested for this investment
        investment.amount_invested = total_invested
        investment.save()

        # Optionally, print logs for debugging
        user = instance.account.account.user
        print(f"Updated total investment amount for {investment.investment_type.name} to {total_invested} for {user.username}")