from django.db import models
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

class Investment(models.Model):
    """
    Represents an investment made by a Sacco. It includes information about the type of investment,
    the amount, the date it was made, and the return on investment (ROI).
    This investment is associated with a specific Sacco.
    """
    name = models.CharField(max_length=255, unique=True)  # Name of the investment
    description = models.TextField(blank=True, null=True)  # A detailed description of the investment
    amount_invested = models.DecimalField(max_digits=15, decimal_places=2)  # Amount invested
    date_invested = models.DateTimeField(default=timezone.now)  # Date the investment was made
    roi_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Return on investment as percentage

    def __str__(self):
        return f"Investment #{self.id} - {self.name}"

    def calculate_roi(self):
        """
        Calculate the return on investment (ROI) for the investment.

        Returns the total amount earned from the investment (original amount + ROI).
        """
        try:
            roi_amount = (self.amount_invested * self.roi_percentage) / 100
            total_return = self.amount_invested + roi_amount
            logger.info(f"Calculated ROI for Investment #{self.id}: {total_return}")
            return total_return
        except Exception as e:
            logger.error(f"Error calculating ROI for Investment #{self.id}: {str(e)}")
            return 0

    def save(self, *args, **kwargs):
        """
        Override the save method to include any necessary calculations or logs before saving the investment.
        """
        logger.info(f"Saving Investment #{self.id}: {self.name} with amount {self.amount_invested} and ROI {self.roi_percentage}")
        super().save(*args, **kwargs)
