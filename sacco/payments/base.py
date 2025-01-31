from abc import ABC, abstractmethod

class BasePaymentService(ABC):
    @abstractmethod
    def initiate_payment(self, phone_number, amount, description, user):
        pass

    @abstractmethod
    def handle_callback(self, data):
        pass

    @abstractmethod
    def initiate_refund(self, payment, refund_amount, phone_number):
        pass