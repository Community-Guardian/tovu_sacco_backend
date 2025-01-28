from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KYCViewSet, AccountViewSet,NextOfKinViewSet

router = DefaultRouter()
router.register(r'kyc', KYCViewSet, basename='kyc')
router.register(r'accounts', AccountViewSet, basename='accounts')
router.register(r'next-of-kins', NextOfKinViewSet, basename='next-of-kins')

urlpatterns = [
    path('api/', include(router.urls)),
]
