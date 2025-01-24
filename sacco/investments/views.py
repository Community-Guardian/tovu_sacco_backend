# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from .models import InvestmentType, Investment, InvestmentAccount, UserInvestment, Dividend
from .serializers import InvestmentTypeSerializer, InvestmentSerializer, InvestmentAccountSerializer, UserInvestmentSerializer, DividendSerializer

class InvestmentTypeViewSet(viewsets.ModelViewSet):
    queryset = InvestmentType.objects.all()
    serializer_class = InvestmentTypeSerializer

class InvestmentViewSet(viewsets.ModelViewSet):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

class InvestmentAccountViewSet(viewsets.ModelViewSet):
    queryset = InvestmentAccount.objects.all()
    serializer_class = InvestmentAccountSerializer

class UserInvestmentViewSet(viewsets.ModelViewSet):
    queryset = UserInvestment.objects.all()
    serializer_class = UserInvestmentSerializer

class DividendViewSet(viewsets.ModelViewSet):
    queryset = Dividend.objects.all()
    serializer_class = DividendSerializer

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
