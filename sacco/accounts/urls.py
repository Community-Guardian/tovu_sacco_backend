from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KYCViewSet, AccountViewSet

router = DefaultRouter()
router.register(r'kyc', KYCViewSet, basename='kyc')
router.register(r'accounts', AccountViewSet, basename='accounts')

urlpatterns = [
    path('api/', include(router.urls)),
]
