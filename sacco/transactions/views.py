import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from .models import TransferTransaction, WithdrawTransaction, RefundTransaction, PaymentRequestTransaction, DepositTransaction
from .serializers import TransferTransactionSerializer, WithdrawTransactionSerializer, RefundTransactionSerializer, PaymentRequestTransactionSerializer, DepositTransactionSerializer

# Configure logging
logger = logging.getLogger(__name__)

class TransferTransactionViewSet(viewsets.ModelViewSet):
    queryset = TransferTransaction.objects.all()
    serializer_class = TransferTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class WithdrawTransactionViewSet(viewsets.ModelViewSet):
    queryset = WithdrawTransaction.objects.all()
    serializer_class = WithdrawTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class RefundTransactionViewSet(viewsets.ModelViewSet):
    queryset = RefundTransaction.objects.all()
    serializer_class = RefundTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentRequestTransactionViewSet(viewsets.ModelViewSet):
    queryset = PaymentRequestTransaction.objects.all()
    serializer_class = PaymentRequestTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class DepositTransactionViewSet(viewsets.ModelViewSet):
    queryset = DepositTransaction.objects.all()
    serializer_class = DepositTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]