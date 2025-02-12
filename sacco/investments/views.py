from rest_framework import viewsets,filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import InvestmentType, Investment, InvestmentAccount, UserInvestment, Dividend
from .serializers import InvestmentTypeSerializer, InvestmentSerializer, InvestmentAccountSerializer, UserInvestmentSerializer, DividendSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import InvestmentFilter, DividendFilter, InvestmentAccountFilter , UserInvestmentFilter

class InvestmentTypeViewSet(viewsets.ModelViewSet):
    queryset = InvestmentType.objects.all()
    serializer_class = InvestmentTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]  # Ensure correct filter backend import
    filterset_class = InvestmentFilter
    ordering_fields = ["name", "created_at", "updated_at"]  # Use 'date_joined' (from AbstractUser) 
    ordering = ["-created_at"]  # Default ordering by newest users first



class InvestmentViewSet(viewsets.ModelViewSet):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer


class InvestmentAccountViewSet(viewsets.ModelViewSet):
    queryset = InvestmentAccount.objects.all()
    serializer_class = InvestmentAccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InvestmentAccountFilter
    search_fields = ['account', 'name']
    ordering_fields = ['account', 'name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Limit the investment account to the user's account if the user is a customer.
        """
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(account__user=user)
        return self.queryset

class UserInvestmentViewSet(viewsets.ModelViewSet):
    queryset = UserInvestment.objects.all()
    serializer_class = UserInvestmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserInvestmentFilter
    search_fields = ['account', 'investment']
    ordering_fields = ['account', 'investment', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Limit user investments to the ones associated with the user's account if the user is a customer.
        """
        user = self.request.user
        if user.role == 'customer':
            return self.queryset.filter(account__account__user=user)
        return self.queryset

class DividendViewSet(viewsets.ModelViewSet):
    queryset = Dividend.objects.all()
    serializer_class = DividendSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = DividendFilter
    ordering = ["-date"]

    def get_queryset(self):
        """
        Limit the dividends to the ones related to the user's investment account if the user is a customer.
        """
        user = self.request.user
        if user.role == 'customer':
            investment_account_ids = InvestmentAccount.objects.filter(account__user=user).values_list('id', flat=True)
            return self.queryset.filter(investment_account__in=investment_account_ids)
        return self.queryset

    def create(self, request, *args, **kwargs):
        """
        Custom create view for dividend to handle calculation
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            dividend = serializer.save()
            dividend.calculate_dividend  # Calculate the dividend before saving
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
