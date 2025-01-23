from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Loan, LoanType, LoanRequirement, LoanPayment, UserLoanRequirement
from .serializers import (
    LoanSerializer,
    LoanTypeSerializer,
    LoanRequirementSerializer,
    LoanPaymentSerializer,
    UserLoanRequirementSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


class LoanTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing loan types.
    """
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer
    permission_classes = [IsAuthenticated]


class LoanRequirementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing loan requirements.
    """
    queryset = LoanRequirement.objects.all()
    serializer_class = LoanRequirementSerializer
    permission_classes = [IsAuthenticated]

class LoanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing loans.
    """
    queryset = Loan.objects.select_related("account", "loan_type")\
        .prefetch_related("loan_type__requirements")  # Prefetch requirements from LoanType
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class UserLoanRequirementView(APIView):
    """
    API endpoint to view and update user loan requirements.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve loan requirements for the authenticated user.
        """
        user_requirements = UserLoanRequirement.objects.filter(account__user=request.user)
        serializer = UserLoanRequirementSerializer(user_requirements, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        """
        Partially update a specific loan requirement for the user.
        """
        requirement = get_object_or_404(UserLoanRequirement, id=pk, account__user=request.user)
        serializer = UserLoanRequirementSerializer(requirement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
