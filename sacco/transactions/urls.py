# sacco/transactions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransferTransactionViewSet, WithdrawTransactionViewSet, RefundTransactionViewSet, DepositTransactionViewSet, LoanTransactionViewSet, InvestmentTransactionViewSet, SavingTransactionViewSet, MinimumSharesDepositTransactionViewSet, AuditTransactionViewSet
from .views import MpesaCallbackView

router = DefaultRouter()
router.register(r'transfers', TransferTransactionViewSet, basename='transfers')
router.register(r'withdrawals', WithdrawTransactionViewSet, basename='withdrawals')
router.register(r'refunds', RefundTransactionViewSet, basename='refunds')
router.register(r'deposits', DepositTransactionViewSet, basename='deposits')
router.register(r'loans', LoanTransactionViewSet, basename='loans')
router.register(r'investments', InvestmentTransactionViewSet, basename='investments')
router.register(r'savings', SavingTransactionViewSet, basename='savings')
router.register(r'minimum_shares_deposits', MinimumSharesDepositTransactionViewSet, basename='minimum_shares_deposits')
router.register(r'audits', AuditTransactionViewSet, basename='audits')

urlpatterns = [
    path('transactions/', include(router.urls)),
    path('mpesa_callback/', MpesaCallbackView.as_view(), name='mpesa_callback'),
]