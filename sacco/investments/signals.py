from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import InvestmentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InvestmentAccount, Dividend, InvestmentType, UserInvestment
from accounts.models import Account
from decimal import Decimal

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

# Signal to update the dividends based on the investments@receiver(post_save, sender=UserInvestment)
def update_dividend_distribution(sender, instance, created, **kwargs):
    if created:
        # Fetch the corresponding Dividend instance, ensuring it's properly initialized
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

                # Access user through the related account, not directly through InvestmentAccount
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
