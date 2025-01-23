from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestmentViewSet

# Create a router and register the InvestmentViewSet
router = DefaultRouter()
router.register(r'investments', InvestmentViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Automatically routes the investment-related views
]
