# sacco/payments/factory.py
from .mpesa import MpesaPaymentService

class PaymentServiceFactory:
    @staticmethod
    def get_payment_service(payment_method):
        if payment_method == "mpesa":
            return MpesaPaymentService()
        # Add other payment services here
        else:
            raise ValueError(f"Unsupported payment method: {payment_method}")