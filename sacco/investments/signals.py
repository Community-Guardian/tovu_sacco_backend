from django.db.models.signals import post_save, pre_save, post_delete, post_migrate
from django.dispatch import receiver
from django.db import transaction, models
from decimal import Decimal
from threading import local
from .models import Investment, InvestmentAccount, Dividend, InvestmentType, UserInvestment
from accounts.models import Account
from django.db.models import Sum
import logging
logger = logging.getLogger(__name__)

# ✅ Thread-local storage to track recursion per request
_recursion_tracker = local()

# 🏦 1. Create InvestmentAccount and Default Dividends when an Account is created
@receiver(post_save, sender=Account)
def create_investment_account(sender, instance, created, **kwargs):
    if created:
        investment_account = InvestmentAccount.objects.create(account=instance)

        # Create dividend records for all investment types
        for investment_type in InvestmentType.objects.all():
            Dividend.objects.create(
                investment_account=investment_account,
                investment_type=investment_type,
                amount=Decimal('0.00'),
                is_distributed=False
            )
        logger.info(f"Investment Account & Dividends created for {instance.user.username}")

# 📊 2. Ensure investment limit is not exceeded before saving
@receiver(pre_save, sender=UserInvestment)
def check_investment_limit(sender, instance, **kwargs):
    investment_account = instance.account
    total_invested = investment_account.user_investments.filter(investment__is_active=True).aggregate(
        total=models.Sum('invested_amount')
    )['total'] or Decimal('0.00')

    new_total_investment = total_invested + instance.invested_amount
    if new_total_investment > investment_account.investment_limit:
        raise ValueError(f"Investment exceeds limit of {investment_account.investment_limit}")

# 🔄 3. Track old invested amount before updating UserInvestment
@receiver(pre_save, sender=UserInvestment)
def track_old_invested_amount(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = UserInvestment.objects.get(pk=instance.pk)
            instance._old_invested_amount = old_instance.invested_amount
        except UserInvestment.DoesNotExist:
            instance._old_invested_amount = Decimal("0.00")
    else:
        instance._old_invested_amount = Decimal("0.00")

# 📈 4. Update total investment & profit/loss on UserInvestment create/update/delete
@receiver(post_save, sender=UserInvestment)
@receiver(post_delete, sender=UserInvestment)
def update_investment_account_balance(sender, instance, **kwargs):
    if getattr(_recursion_tracker, "account_update", False):
        return  # Prevent recursion

    _recursion_tracker.account_update = True  # Mark as processing

    try:
        investment_account = instance.account
        total_investments = investment_account.user_investments.filter(investment__is_active=True).aggregate(
            total=models.Sum('invested_amount')
        )['total'] or Decimal('0.00')

        total_profit_or_loss = sum(
            user_investment.investment.profit_or_loss
            for user_investment in investment_account.user_investments.all()
        )

        with transaction.atomic():
            investment_account.total_investments = total_investments
            investment_account.total_profit_or_loss = total_profit_or_loss
            investment_account.save(update_fields=["total_investments", "total_profit_or_loss"])
        
    finally:
        _recursion_tracker.account_update = False  # Reset flag

# 💰 5. Update dividend amount when a UserInvestment is created or updated
@receiver(post_save, sender=UserInvestment)
@receiver(post_delete, sender=UserInvestment)
def update_dividend_distribution(sender, instance, **kwargs):
    if getattr(_recursion_tracker, "dividend_update", False):
        return  # Prevent recursion

    _recursion_tracker.dividend_update = True  # Mark as processing

    try:

         with transaction.atomic():
            dividend = Dividend.objects.filter(
                investment_account=instance.account,
                investment_type=instance.investment.investment_type
            ).first()

            if dividend:
                # Recalculate dividend for each user investment in the same investment type
                user_investments = UserInvestment.objects.filter(
                    investment__investment_type=instance.investment.investment_type,
                    account=instance.account
                )
                
                total_invested = user_investments.aggregate(
                    total=Sum('invested_amount')
                )['total'] or Decimal('0.00')

                if total_invested > Decimal('0.00'):
                    # Update the dividend amount for each user investment
                    total_dividend = Decimal('0.00')
                    for user_investment in user_investments:
                        user_share = dividend.calculate_user_dividend_share(user_investment)
                        total_dividend += user_share

                    # Ensure total_dividend is Decimal and update the dividend amount
                    dividend.amount = total_dividend
                    dividend.save(update_fields=["amount"])
                    logger.info(f"Dividend updated for {instance.account.account.user.username}")
                else:
                    logger.info(f"No investments to calculate dividend for {instance.account.account.user.username}")
            else:
                logger.info(f"No dividend found for {instance.account.account.user.username}")

    finally:
        _recursion_tracker.dividend_update = False  # Reset flag

# 💹 6. Auto-update profit/loss & investment value when Investment changes
@receiver(post_save, sender=Investment)
def update_investment_profit_loss(sender, instance, **kwargs):
    if getattr(_recursion_tracker, "profit_loss_update", False):
        return  # Prevent recursion

    _recursion_tracker.profit_loss_update = True  # Mark as processing

    try:
        for user_investment in UserInvestment.objects.filter(investment=instance):
            investment_account = user_investment.account

            total_profit_or_loss = sum(
                user_investment.investment.profit_or_loss
                for user_investment in investment_account.user_investments.all()
            )

            with transaction.atomic():
                investment_account.total_profit_or_loss = total_profit_or_loss
                investment_account.save(update_fields=["total_profit_or_loss"])
    finally:
        _recursion_tracker.profit_loss_update = False  # Reset flag

# 🔄 7. Automatically distribute dividends when marked as distributed
@receiver(post_save, sender=Dividend)
def update_investment_account_after_dividend(sender, instance, **kwargs):
    if instance.is_distributed:
        for user_investment in instance.investment_account.user_investments.all():
            investment_account = user_investment.account

            total_profit_or_loss = sum(
                user_investment.investment.profit_or_loss
                for user_investment in investment_account.user_investments.all()
            )

            with transaction.atomic():
                investment_account.total_profit_or_loss = total_profit_or_loss
                investment_account.save(update_fields=["total_profit_or_loss"])

# 🏦 8. Ensure total investment per Investment is updated when a new UserInvestment is made
@receiver(post_save, sender=UserInvestment)
def update_investment_total(sender, instance, created, **kwargs):
    if created:
        investment = instance.investment

        total_invested = investment.linked_user_investments.aggregate(
            total=models.Sum('invested_amount')
        )['total'] or Decimal('0.00')

        with transaction.atomic():
            investment.amount_invested = total_invested
            investment.save(update_fields=["amount_invested"])

        logger.info(f"Updated total investment for {investment.investment_type.name} to {total_invested}")

# 🔄 9. Update Investment current value based on ROI
@receiver(pre_save, sender=Investment)
def update_current_value(sender, instance, **kwargs):
    """
    Before saving the Investment, update the current_value based on ROI.
    This ensures that current_value is always correct.
    """
    if instance.pk:  # Check if the instance exists (not a new investment)
        old_instance = Investment.objects.get(pk=instance.pk)
        
        # Update only if ROI or amount_invested has changed
        if old_instance.return_on_investment != instance.return_on_investment or old_instance.amount_invested != instance.amount_invested:
            instance.current_value = instance.calculate_current_value()

# 🛠 10. Populate sample InvestmentTypes after migration
@receiver(post_migrate)
def create_sample_investment_types(sender, **kwargs):
    if sender.name == "investments":
        investment_types = [
            {"name": "Real Estate"}, {"name": "Stock Market"}, {"name": "Cryptocurrency"},
            {"name": "Bonds"}, {"name": "Mutual Funds"}
        ]
        for data in investment_types:
            InvestmentType.objects.get_or_create(name=data["name"])

