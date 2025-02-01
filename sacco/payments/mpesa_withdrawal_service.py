import logging
from datetime import datetime
from django_daraja.mpesa.core import MpesaClient
from transactions.models import WithdrawTransaction
from django.db.transaction import atomic  # Import the transaction module
from django.utils import timezone
logger = logging.getLogger('mpesa_withdrawal_service')

class MpesaWithdrawalService:
    @staticmethod
    def initiate_withdrawal(phone_number, amount, description="Withdrawal via M-Pesa", user=None):
        cl = MpesaClient()
        try:
            logger.info(f"Initiating M-Pesa withdrawal of {amount} KES to {phone_number}.")
            response = cl.b2c_payment(
                phone_number=phone_number,
                amount=amount,
                transaction_desc=description,
                callback_url="https://tovusacco2.pythonanywhere.com/mpesa_callback/",
                occassion="Withdrawal"
            )
            response_data = response.json()
            if response.status_code != 200:
                logger.error(f"M-Pesa withdrawal initiation failed: {response_data}")
                raise ValueError("Failed to initiate M-Pesa withdrawal.")

            transaction = WithdrawTransaction.objects.create(
                user=user,
                amount=amount,
                description=description,
                status="processing",
                payment_method="mpesa",
                transaction_type="withdraw",
                mpesa_transaction_id=response_data.get("TransactionID"),
                mpesa_phone_number=phone_number,
            )
            logger.info(f"M-Pesa withdrawal initiated, transaction ID: {transaction.transaction_id}")
            return transaction

        except Exception as e:
            logger.error(f"Error initiating M-Pesa withdrawal: {e}")
            raise

    @staticmethod
    def handle_withdrawal_callback(data):
        if not data:
            logger.warning("Empty callback data received.")
            return

        try:
            b2c_callback = data.get("Result", {})
            result_code = b2c_callback.get("ResultCode")
            result_desc = b2c_callback.get("ResultDesc")
            transaction_id = b2c_callback.get("TransactionID")
            callback_metadata = b2c_callback.get("ResultParameters", {}).get("ResultParameter", [])

            if not transaction_id:
                logger.error("Missing TransactionID in callback data.")
                return

            transaction = WithdrawTransaction.objects.get(mpesa_transaction_id=transaction_id)

            with atomic():
                transaction.mpesa_result_code = result_code
                transaction.mpesa_result_desc = result_desc

                if result_code == 0:  # Success
                    for item in callback_metadata:
                        if item["Key"] == "TransactionAmount":
                            transaction.amount = item["Value"]
                        elif item["Key"] == "TransactionReceipt":
                            transaction.mpesa_transaction_id = item["Value"]
                        elif item["Key"] == "TransactionCompletedDateTime":
                            transaction.update = timezone.make_aware(datetime.strptime(str(item["Value"]), "%d.%m.%Y %H:%M:%S"))
                        elif item["Key"] == "ReceiverPartyPublicName":
                            transaction.mpesa_phone_number = item["Value"]

                    # Ensure account balance does not go negative
                    account = transaction.account
                    if account.account_balance < transaction.amount:
                        logger.error(f"Insufficient funds for transaction {transaction.transaction_id}")
                        transaction.status = "failed"
                    else:
                        account.save()
                        transaction.status = "completed"
                else:
                    transaction.status = "failed"

                transaction.save()

            logger.info(f"M-Pesa withdrawal callback processed for transaction ID: {transaction.transaction_id}")
        except WithdrawTransaction.DoesNotExist:
            logger.error(f"Transaction with TransactionID {transaction_id} not found.")
        except Exception as e:
            logger.error(f"Error processing M-Pesa withdrawal callback: {e}")