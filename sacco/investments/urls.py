# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestmentTypeViewSet, InvestmentViewSet, InvestmentAccountViewSet, UserInvestmentViewSet, DividendViewSet

router = DefaultRouter()
router.register(r'investment-types', InvestmentTypeViewSet)
router.register(r'investments', InvestmentViewSet)
router.register(r'investment-accounts', InvestmentAccountViewSet)
router.register(r'user-investments', UserInvestmentViewSet)
router.register(r'dividends', DividendViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
