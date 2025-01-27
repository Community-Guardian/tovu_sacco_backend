from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from .models import BaseTransaction, TransferTransaction, WithdrawTransaction, RefundTransaction, DepositTransaction
from .serializers import (
    BaseTransactionSerializer,
    TransferTransactionSerializer,
    WithdrawTransactionSerializer,
    RefundTransactionSerializer,
    DepositTransactionSerializer
)

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

    @action(detail=False, methods=['post'])
    def create_withdraw(self, request):
        data = request.data.copy()  # Create a mutable copy
        if 'user' not in data:
            data['user'] = request.user.id  # Add the user to the data
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save with the logged-in user
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


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


# Optional: A custom action to handle querying by status or other filters
class TransactionStatusViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def filter_by_status(self, request):
        status = request.query_params.get('status', None)
        if not status:
            raise NotFound(detail="Status parameter is required.")
        
        transactions = BaseTransaction.objects.filter(status=status, user=request.user)
        serializer = BaseTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
