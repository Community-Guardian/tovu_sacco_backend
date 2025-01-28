from rest_framework import viewsets, permissions,status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound,ValidationError
from django.shortcuts import get_object_or_404
from .models import BaseTransaction, TransferTransaction, WithdrawTransaction, RefundTransaction, DepositTransaction
from .serializers import (
    BaseTransactionSerializer,
    TransferTransactionSerializer,
    WithdrawTransactionSerializer,
    RefundTransactionSerializer,
    DepositTransactionSerializer
)
from accounts.models import Account
from django.db.models import Q

class TransferTransactionViewSet(viewsets.ModelViewSet):
    queryset = TransferTransaction.objects.all()
    serializer_class = TransferTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_transfer(self, request):
        data = request.data.copy()  # Create a mutable copy
        if 'user' not in data:
            data['user'] = request.user.id  # Add the user to the data
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save with the logged-in user
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
class WithdrawTransactionViewSet(viewsets.ModelViewSet):
    queryset = WithdrawTransaction.objects.all()
    serializer_class = WithdrawTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Ensure the user is assigned to the transaction
        if 'user' not in data:
            data['user'] = request.user.id

        # Validate that the account exists and belongs to the user
        try:
            account_id = int(data.get('account', 0))  # Ensure the ID is an integer
            account = Account.objects.get(pk=account_id, user=request.user)
        except ValueError:
            return Response({"detail": "Invalid account ID."}, status=status.HTTP_400_BAD_REQUEST)
        except Account.DoesNotExist:
            return Response({"detail": "Invalid account or the account does not belong to the user."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate withdrawal amount against account balance
        try:
            withdrawal_amount = int(data.get('amount', 0))
            if withdrawal_amount <= 0:
                return Response({"detail": "Withdrawal amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)
            if withdrawal_amount > account.account_balance:
                return Response({"detail": f"Withdrawal amount ({withdrawal_amount}) exceeds account balance ({account.account_balance})."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "Invalid withdrawal amount."}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize and save the transaction
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save with the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class RefundTransactionViewSet(viewsets.ModelViewSet):
    queryset = RefundTransaction.objects.all()
    serializer_class = RefundTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_refund(self, request):
        data = request.data.copy()  # Create a mutable copy
        if 'user' not in data:
            data['user'] = request.user.id  # Add the user to the data
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save with the logged-in user
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class DepositTransactionViewSet(viewsets.ModelViewSet):
    queryset = DepositTransaction.objects.all()
    serializer_class = DepositTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_deposit(self, request):
        data = request.data.copy()  # Create a mutable copy
        if 'user' not in data:
            data['user'] = request.user.id  # Add the user to the data
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save with the logged-in user
            serializer.save(status='pending')  # Set status as pending
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TransactionStatusViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def filter_by_status(self, request):
        # Get the 'status' parameter from the request
        status = request.query_params.get('status', None)
        if not status:
            raise NotFound(detail="Status parameter is required.")
        
        # Fetch transactions based on status for each concrete model
        transfer_transactions = TransferTransaction.objects.filter(status=status, user=request.user)
        withdraw_transactions = WithdrawTransaction.objects.filter(status=status, user=request.user)
        refund_transactions = RefundTransaction.objects.filter(status=status, user=request.user)
        deposit_transactions = DepositTransaction.objects.filter(status=status, user=request.user)

        # Combine the results manually
        transactions = list(transfer_transactions) + list(withdraw_transactions) + list(refund_transactions) + list(deposit_transactions)

        # Serialize the results
        # Here you can choose which serializer to use based on the model
        # You may serialize each one based on its model if necessary, or use a common serializer
        if transactions:
            if isinstance(transactions[0], TransferTransaction):
                serializer = TransferTransactionSerializer(transactions, many=True)
            elif isinstance(transactions[0], WithdrawTransaction):
                serializer = WithdrawTransactionSerializer(transactions, many=True)
            elif isinstance(transactions[0], RefundTransaction):
                serializer = RefundTransactionSerializer(transactions, many=True)
            elif isinstance(transactions[0], DepositTransaction):
                serializer = DepositTransactionSerializer(transactions, many=True)
            
            return Response(serializer.data)
        else:
            return Response([])