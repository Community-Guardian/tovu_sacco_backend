from rest_framework import viewsets
from .models import Loan, LoanType, LoanRequirement, LoanPayment, UserLoanRequirement, LoanHistory
from .serializers import (
    LoanSerializer,
    LoanTypeSerializer,
    LoanRequirementSerializer,
    LoanPaymentSerializer,
    UserLoanRequirementSerializer,
    LoanHistorySerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework import status,filters
import logging
from rest_framework.exceptions import ValidationError
from django.db import models
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import LoanFilter, LoanHistoryFilter, LoanPaymentFilter 

logger = logging.getLogger(__name__)

class LoanTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing loan types.
    """
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer




class LoanRequirementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing loan requirements.
    """
    queryset = LoanRequirement.objects.all()
    serializer_class = LoanRequirementSerializer



class LoanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing loans.
    """
    queryset = Loan.objects.select_related("account", "loan_type")\
        .prefetch_related("loan_type__requirements")  # Prefetch requirements from LoanType
    serializer_class = LoanSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LoanFilter
    ordering_fields = ["amount_requested", "date_requested", "date_approved"]
    ordering = ["-date_requested"]



    def get_queryset(self):
        """
        If the user is a customer, only return loans related to the authenticated user's account.
        """
        user = self.request.user
        if user.role == "customer":  # Assuming "role" is the field used to define user roles
            return Loan.objects.filter(account=user.account)
        return Loan.objects.all()  # Admin or any other role has access to all loans

    def perform_create(self, serializer):  
        serializer.save(account=self.request.user.account)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """
        Custom action to approve a loan.
        """
        user = request.user
        if not user.is_staff:
            return Response({"error": "Only Admins can approve loans."}, status=HTTP_400_BAD_REQUEST)
        loan = self.get_object()
        try:
            loan.approvee = user
            loan.approve_loan()
            return Response({"message": "Loan approved successfully."}, status=HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def calculate_interest(self, request, pk=None):
        """
        Calculate the total interest for a loan.
        """
        loan = self.get_object()
        total_interest = loan.calculate_interest()
        return Response({"loan_id": loan.id, "total_interest": total_interest}, status=HTTP_200_OK)


class LoanPaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing loan payments.
    """
    queryset = LoanPayment.objects.select_related("loan")
    serializer_class = LoanPaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LoanPaymentFilter
    ordering_fields = ["amount", "payment_date"]
    ordering = ["-payment_date"]


    def get_queryset(self):
        """
        If the user is a customer, only return payments related to the authenticated user's loans.
        """
        user = self.request.user
        if user.role == "customer":  # Assuming "role" is the field used to define user roles
            return LoanPayment.objects.filter(loan__account=user.account)
        return LoanPayment.objects.all()  # Admin or any other role has access to all loan payments

    def perform_create(self, serializer):
        # Get the loan instance related to the payment
        loan = serializer.validated_data['loan']

        # Check if the loan is approved and has a valid amount_approved
        if loan.amount_approved is None:
            raise ValidationError("Loan has not been approved or does not have a valid loan amount.")

        # Calculate the total payments made so far for this loan
        total_payments = loan.payments.aggregate(total_paid=models.Sum('amount'))['total_paid'] or 0

        # Check if the new payment would exceed the loan balance
        remaining_balance = loan.amount_approved - total_payments

        if serializer.validated_data['amount'] > remaining_balance:
            raise ValidationError(f"The payment amount exceeds the remaining loan balance of {remaining_balance:.2f}")

        # If the payment is valid, save it
        serializer.save()

    def create(self, request, *args, **kwargs):
        # Override the create method to handle the response after saving the payment
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLoanRequirementViewSet(viewsets.ModelViewSet):
    """
    API endpoint to view and update user loan requirements.
    """
    queryset = UserLoanRequirement.objects.all()
    serializer_class = UserLoanRequirementSerializer


    # Restricting allowed HTTP methods to GET and PATCH only
    http_method_names = ['get', 'patch']  # Only allow GET and PATCH methods

    def get_queryset(self):
        """
        Ensure that users can only see their own loan requirements.
        """
        return UserLoanRequirement.objects.filter(account__user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific loan requirement for the authenticated user.
        """
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a specific loan requirement for the authenticated user.
        """
        instance = self.get_object()
        if instance.account.user != request.user:
            return Response({"error": "You are not authorized to update this requirement."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)


class LoanHistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for retrieving loan history.
    Supports filtering by loan_id and ordering by timestamp.
    """
    queryset = LoanHistory.objects.all().order_by("-timestamp")
    serializer_class = LoanHistorySerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LoanHistoryFilter
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]
