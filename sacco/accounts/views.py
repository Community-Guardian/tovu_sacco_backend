from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import KYC, Account,NextOfKin
from .serializers import KYCSerializer, AccountSerializer,NextOfKinSerializer
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

class KYCViewSet(viewsets.ModelViewSet):
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer

    def get_queryset(self):
        user = self.request.user
        return KYC.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        # Create a mutable copy of request.data
        data = request.data.copy()

        data['user'] = request.user.id
        
        # Proceed with creating the object using the modified data
        request._full_data = data  # Override the original request data with the mutable data

        return super().create(request, *args, **kwargs)
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        # Ensure that KYC exists before account creation
        if not KYC.objects.filter(user=request.user).exists():
            return Response({"detail": "KYC information is required."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
class NextOfKinViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing NextOfKin records.
    """
    queryset = NextOfKin.objects.all()
    serializer_class = NextOfKinSerializer

    def get_queryset(self):
        # Restrict to NextOfKin records related to the current user's KYC
        user = self.request.user
        return NextOfKin.objects.filter(kyc__user=user)

    def perform_create(self, serializer):
        # Automatically associate the current user's KYC record
        kyc = KYC.objects.get(user=self.request.user)
        serializer.save(kyc=kyc)

