from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from .models import KYC, Account, NextOfKin
from .serializers import KYCSerializer, AccountSerializer, NextOfKinSerializer,CustomUserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import NextOfKinFilter, KYCFilter, AccountFilter

class KYCViewSet(viewsets.ModelViewSet):
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = KYCFilter
    search_fields = ['membership_number', 'id_number', 'kra_pin']
    ordering_fields = ['membership_number', 'id_number', 'kra_pin', 'marital_status', 'gender', 'kyc_submitted', 'kyc_confirmed']
    ordering = ['-kyc_submitted']

    def get_queryset(self):
        user = self.request.user
        # Only show KYC records for the authenticated user
        if user.role == 'customer':
            return KYC.objects.filter(user=user)
        return self.queryset  # Admin or any other role has access to all KYC records

    def create(self, request, *args, **kwargs):
        # Create a mutable copy of request.data
        data = request.data.copy()
        user = request.user
        if user.role == 'customer':
            data['user'] = request.user.id  # Automatically assign the user to the KYC record
        if not data.get('user'):
            return Response({"detail": "User is required."}, status=status.HTTP_400_BAD_REQUEST)
        # Proceed with creating the object using the modified data
        request._full_data = data  # Override the original request data with the mutable data

        return super().create(request, *args, **kwargs)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AccountFilter
    search_fields = ['account_number', 'branch', 'account_type']
    ordering_fields = ['account_number', 'branch', 'account_type', 'created_at', 'updated_at']
    ordering = ['-created']

    def get_queryset(self):
        user = self.request.user
        # Only show account records for the authenticated user
        if user.role == 'customer':
            return Account.objects.filter(user=user)
        return self.queryset  # Admin or any other role has access to all accounts

    def create(self, request, *args, **kwargs):
        # Custom logic for account creation (e.g., ensure KYC exists)
        if not KYC.objects.filter(user=request.user).exists():
            return Response({"detail": "KYC information is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Proceed with account creation
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the account instance to update
        data = request.data  # Get the data sent in the request

        # Update or handle nested data (e.g., `kyc` and `user` models)
        # Create or update kyc and user if provided
        kyc_data = data.get("kyc", None)
        user_data = data.get("user", None)

        if kyc_data:
            # Handle kyc update or creation here (e.g., using a serializer for kyc)
            pass

        if user_data:
            # Handle user update or creation here (e.g., using a serializer for user)
            pass

        # Handle other updates on Account model fields
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save the updated instance

        return Response(serializer.data)  # Return the updated data
    def partial_update(self, request, *args, **kwargs):
        # Get the object instance that will be updated
        instance = self.get_object()

        # Get the data from the request (it will contain the fields to be updated)
        data = request.data

        # Handling the nested `kyc` data if provided
        kyc_data = data.get('kyc', None)
        if kyc_data:
            # Validate and update the KYC nested data
            kyc_serializer = KYCSerializer(instance.kyc, data=kyc_data, partial=True, context={'request': request})
            kyc_serializer.is_valid(raise_exception=True)
            kyc_serializer.save()

            # Remove `kyc` from the data to ensure it's not passed to the Account serializer
            data.pop('kyc', None)

        # Handling the nested `user` data if provided
        user_data = data.get('user', None)
        if user_data:
            # Validate and update the User nested data
            user_serializer = CustomUserSerializer(instance.user, data=user_data, partial=True, context={'request': request})
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            # Remove `user` from the data to ensure it's not passed to the Account serializer
            data.pop('user', None)

        # Now, handle the remaining fields for the Account model
        # We pass `partial=True` to allow updating only the provided fields
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save the updated instance

        # Return the updated data in the response
        return Response(serializer.data)
class NextOfKinViewSet(viewsets.ModelViewSet):
    queryset = NextOfKin.objects.all()
    serializer_class = NextOfKinSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NextOfKinFilter
    search_fields = ['name', 'relationship', 'phone_number']
    ordering_fields = ['name', 'relationship', 'phone_number', 'kyc__created_at', 'kyc__updated_at']
    ordering = ['-kyc__created_at']

    def get_queryset(self):
        user = self.request.user
        # Restrict to NextOfKin records related to the current user's KYC
        if user.role == 'customer':
            return NextOfKin.objects.filter(kyc__user=user)
        return self.queryset  # Admin or any other role has access to all NextOfKin records

    def perform_create(self, serializer):
        # Automatically associate the current user's KYC record
        kyc = KYC.objects.get(user=self.request.user)
        serializer.save(kyc=kyc)
