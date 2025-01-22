from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, KYCViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'kyc', KYCViewSet, basename='kyc')

urlpatterns = [
    path('', include(router.urls)),
]
