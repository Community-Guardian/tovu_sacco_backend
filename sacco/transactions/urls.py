from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransferTransactionViewSet,
    WithdrawTransactionViewSet,
    RefundTransactionViewSet,
    DepositTransactionViewSet,
    TransactionStatusViewSet
)

router = DefaultRouter()
router.register(r'transfers', TransferTransactionViewSet, basename='transfers')
router.register(r'withdrawals', WithdrawTransactionViewSet, basename='withdrawals')
router.register(r'refunds', RefundTransactionViewSet, basename='refunds')
router.register(r'deposits', DepositTransactionViewSet, basename='deposits')
router.register(r'transaction_status', TransactionStatusViewSet, basename='transaction_status')

urlpatterns = [
    path('', include(router.urls)),
]
