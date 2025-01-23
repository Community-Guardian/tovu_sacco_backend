import logging
from datetime import datetime
from django_daraja.mpesa.core import MpesaClient

from transactions.models import DepositTransaction,RefundTransaction

logger = logging.getLogger('mpesa_services')

class MpesaServices:
    @staticmethod
    def initiate_mpesa_payment(phone_number, amount, description="Payment via M-Pesa", user=None):
        cl = MpesaClient()
        try:
            logger.info(f"Initiating M-Pesa payment for {amount} KES to {phone_number}.")
            response = cl.stk_push(
                phone_number=phone_number,
                amount=amount,
                account_reference="Swift-Traders",
                transaction_desc=description,
                callback_url="https://api.swift-traders.co.ke/callback/"
            )
            response_data = response.json()
            if response.status_code != 200:
                logger.error(f"M-Pesa payment initiation failed: {response_data}")
                raise ValueError("Failed to initiate M-Pesa payment.")

            transaction = DepositTransaction.objects.create(
                user=user,
                amount=amount,
                description=description,
                status="pending",
                payment_method="mpesa",
                transaction_type="deposit",
                mpesa_checkout_request_id=response_data.get("CheckoutRequestID"),
                mpesa_merchant_request_id=response_data.get("MerchantRequestID"),
                mpesa_phone_number=phone_number,
            )
            logger.info(f"M-Pesa payment initiated, transaction ID: {transaction.transaction_id}")
            return transaction

        except Exception as e:
            logger.error(f"Error initiating M-Pesa payment: {e}")
            raise

    @staticmethod
    def handle_mpesa_callback(data):
        if not data:
            logger.warning("Empty callback data received.")
            return

        try:
            stk_callback = data.get("Body", {}).get("stkCallback", {})
            merchant_request_id = stk_callback.get("MerchantRequestID")
            result_code = stk_callback.get("ResultCode")
            result_desc = stk_callback.get("ResultDesc")
            callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

            if not merchant_request_id:
                logger.error("Missing MerchantRequestID in callback data.")
                return

            transaction = DepositTransaction.objects.get(mpesa_merchant_request_id=merchant_request_id)

            with transaction.atomic():
                transaction.mpesa_result_code = result_code
                transaction.mpesa_result_desc = result_desc

                if result_code == 0:  # Success
                    for item in callback_metadata:
                        if item["Name"] == "Amount":
                            transaction.amount = item["Value"]
                        elif item["Name"] == "MpesaReceiptNumber":
                            transaction.mpesa_transaction_id = item["Value"]
                        elif item["Name"] == "TransactionDate":
                            transaction.date = datetime.strptime(str(item["Value"]), "%Y%m%d%H%M%S")
                        elif item["Name"] == "PhoneNumber":
                            transaction.mpesa_phone_number = item["Value"]

                    transaction.status = "completed"
                else:
                    transaction.status = "failed"

                transaction.save()

            logger.info(f"M-Pesa callback processed for transaction ID: {transaction.transaction_id}")
        except DepositTransaction.DoesNotExist:
            logger.error(f"Transaction with MerchantRequestID {merchant_request_id} not found.")
        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {e}")

    @staticmethod
    def initiate_refund(payment, refund_amount, phone_number):
        cl = MpesaClient()
        try:
            logger.info(f"Initiating M-Pesa refund of {refund_amount} KES to {phone_number}.")
            response = cl.business_payment(
                phone_number=phone_number,
                amount=refund_amount,
                remarks=f"Refund for transaction {payment.transaction_id}",
                callback_url="https://api.swift-traders.co.ke/result/",
                occasion="Refund"
            )
            response_data = response.json()
            if response.status_code != 200:
                logger.error(f"Refund initiation failed: {response_data}")
                raise ValueError("Failed to initiate refund.")

            refund_transaction = RefundTransaction.objects.create(
                user=payment.user,
                amount=refund_amount,
                description=f"Refund for transaction {payment.transaction_id}",
                status="processing",
                payment_method="mpesa",
                transaction_type="refund",
                mpesa_transaction_id=response_data.get("TransactionID"),
                mpesa_phone_number=phone_number,
            )
            logger.info(f"Refund initiated, transaction ID: {refund_transaction.transaction_id}")
            return refund_transaction

        except Exception as e:
            logger.error(f"Error initiating refund: {e}")
            raise
