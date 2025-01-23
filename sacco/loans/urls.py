from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanViewSet, LoanTypeViewSet, LoanRequirementViewSet, LoanPaymentViewSet , UserLoanRequirement

router = DefaultRouter()
router.register("loans", LoanViewSet, basename="loan")
router.register("loan-types", LoanTypeViewSet, basename="loan-type")
router.register("loan-requirements", LoanRequirementViewSet, basename="loan-requirement")
router.register("loan-payments", LoanPaymentViewSet, basename="loan-payment")

urlpatterns = [
    path("", include(router.urls)),
    path("user-requirements/", UserLoanRequirement, name="user-requirements"),
]
