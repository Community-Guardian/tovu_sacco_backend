from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import KYC, Account
from .serializers import KYCSerializer, AccountSerializer
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

class KYCViewSet(viewsets.ModelViewSet):
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer

    def get_queryset(self):
        user = self.request.user
        return KYC.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        if 'user' not in request.data:
            request.data['user'] = request.user.id
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
