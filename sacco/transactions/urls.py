from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransferTransactionViewSet, WithdrawTransactionViewSet, RefundTransactionViewSet, DepositTransactionViewSet

router = DefaultRouter()
router.register(r'transfers', TransferTransactionViewSet, basename='transfer')
# router.register(r'withdraws', WithdrawTransactionViewSet, basename='withdraw')
# router.register(r'refunds', RefundTransactionViewSet, basename='refund')
router.register(r'deposits', DepositTransactionViewSet, basename='deposit')

urlpatterns = [
    path('', include(router.urls)),
]