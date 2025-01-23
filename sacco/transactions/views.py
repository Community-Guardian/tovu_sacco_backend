from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import (
    TransferTransaction,
    WithdrawTransaction,
    RefundTransaction,
    DepositTransaction,
)
from .serializers import (
    TransferTransactionSerializer,
    WithdrawTransactionSerializer,
    RefundTransactionSerializer,
    DepositTransactionSerializer,
)
from .mpesa_services import MpesaServices  # Import the Mpesa payment service
from accounts.models import Account
from django.db import transaction as db_transaction
import logging

# Configure logging
logger = logging.getLogger(__name__)


class TransferTransactionViewSet(viewsets.ModelViewSet):
    queryset = TransferTransaction.objects.all()
    serializer_class = TransferTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Restrict results to the authenticated user
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        sender_account = data.get("sender_account")
        recipient_account = data.get("recipient_account")
        transfer_amount = data.get("amount")

        if not sender_account or not recipient_account:
            return Response(
                {"error": "Sender and recipient accounts are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if sender_account == recipient_account:
            return Response(
                {"error": "Sender and recipient accounts cannot be the same."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            sender = Account.objects.get(account_number=sender_account)
            recipient = Account.objects.get(account_number=recipient_account)

            if sender.balance < transfer_amount:
                return Response(
                    {"error": "Insufficient funds in sender's account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            transaction = TransferTransaction.objects.create(
                user=request.user,
                sender_account=sender_account,
                recipient_account=recipient_account,
                amount=transfer_amount,
                description=data.get("description", ""),
                transaction_type="transfer",
                payment_method="in-house",
                status="completed",
            )

            serializer = self.get_serializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Account.DoesNotExist:
            return Response(
                {"error": "One or both accounts do not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error processing in-house transfer: {str(e)}")
            return Response(
                {"error": "An error occurred while processing the transfer."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, *args, **kwargs):
        raise NotImplementedError("PUT/PATCH methods are not allowed.")

    def destroy(self, *args, **kwargs):
        raise NotImplementedError("DELETE method is not allowed.")


class WithdrawTransactionViewSet(viewsets.ModelViewSet):
    queryset = WithdrawTransaction.objects.all()
    serializer_class = WithdrawTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def update(self, *args, **kwargs):
        raise NotImplementedError("PUT/PATCH methods are not allowed.")

    def destroy(self, *args, **kwargs):
        raise NotImplementedError("DELETE method is not allowed.")


class RefundTransactionViewSet(viewsets.ModelViewSet):
    queryset = RefundTransaction.objects.all()
    serializer_class = RefundTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def update(self, *args, **kwargs):
        raise NotImplementedError("PUT/PATCH methods are not allowed.")

    def destroy(self, *args, **kwargs):
        raise NotImplementedError("DELETE method is not allowed.")


class DepositTransactionViewSet(viewsets.ModelViewSet):
    queryset = DepositTransaction.objects.all()
    serializer_class = DepositTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        phone_number = data.get("phone_number")
        account = data.get("account")
        amount = data.get("amount")

        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not account:
            return Response({"error": "Account is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not amount or amount <= 0:
            return Response({"error": "A valid deposit amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with db_transaction.atomic():
                transaction = MpesaServices.initiate_mpesa_payment(
                    phone_number=phone_number,
                    amount=amount,
                    description=f"Deposit for account {account}",
                    user=user
                )

            serializer = self.get_serializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.error(f"Validation error during deposit creation: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating deposit transaction: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, *args, **kwargs):
        raise NotImplementedError("PUT/PATCH methods are not allowed.")

    def destroy(self, *args, **kwargs):
        raise NotImplementedError("DELETE method is not allowed.")
