from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanViewSet, LoanTypeViewSet, LoanRequirementViewSet, LoanPaymentViewSet , UserLoanRequirementViewSet, LoanHistoryViewSet

router = DefaultRouter()
router.register("loans", LoanViewSet, basename="loan")
router.register("loan-types", LoanTypeViewSet, basename="loan-type")
router.register("loan-requirements", LoanRequirementViewSet, basename="loan-requirement")
router.register("loan-payments", LoanPaymentViewSet, basename="loan-payment")
router.register("user-requirements", UserLoanRequirementViewSet, basename="user-requirements")
router.register(r"loan-history", LoanHistoryViewSet, basename="loan-history")

urlpatterns = [
    path("", include(router.urls)),
]
