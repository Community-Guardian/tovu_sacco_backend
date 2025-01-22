import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from .models import Account, KYC
from .serializers import AccountSerializer, KYCSerializer

# Configure logging
logger = logging.getLogger(__name__)

class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Account instances.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Limit access to only the user's account unless admin
        user = self.request.user
        if user.is_staff:
            return Account.objects.all()
        return Account.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Account with ID {kwargs['pk']} retrieved successfully.")
            return Response(serializer.data)
        except Account.DoesNotExist:
            logger.error(f"Account with id {kwargs['pk']} not found")
            raise NotFound(detail="Account not found. Please check the account ID.")
        except Exception as e:
            logger.error(f"Error retrieving account: {str(e)}")
            return Response({"detail": {str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            try:
                account = Account.objects.get(id=kwargs['pk'])
            except Account.DoesNotExist:
                raise NotFound(detail="Account not found. Please check the account ID.")
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(f"Account with ID {kwargs['pk']} updated successfully.")
            return Response(serializer.data)
        except Account.DoesNotExist:
            logger.error(f"Account with id {kwargs['pk']} not found")
            raise NotFound(detail="Account not found. Please check the account ID.")
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to update account {kwargs['pk']}")
            raise PermissionDenied(detail="You do not have permission to update this account.")
        except ValidationError as ve:
            logger.error(f"Validation error while updating account {kwargs['pk']}: {str(ve)}")
            return Response({"detail": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error updating account with id {kwargs['pk']}: {str(e)}")
            return Response({"detail": {str(e)} }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not request.user.is_superuser:
                raise PermissionDenied(detail="You do not have permission to delete this account.")
            self.perform_destroy(instance)
            logger.info(f"Account with ID {kwargs['pk']} deleted successfully.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Account.DoesNotExist:
            logger.error(f"Account with id {kwargs['pk']} not found")
            raise NotFound(detail="Account not found. Please check the account ID.")
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to delete account {kwargs['pk']}")
            raise PermissionDenied(detail="You do not have permission to delete this account.")
        except Exception as e:
            logger.error(f"Unexpected error deleting account with id {kwargs['pk']}: {str(e)}")
            return Response({"detail": {str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KYCViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing KYC instances.
    """
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get the user and base queryset
        user = self.request.user
        queryset = KYC.objects.all() if user.is_staff else KYC.objects.filter(user=user)
        
        # Retrieve query parameters
        status = self.request.query_params.get('status', None)
        country = self.request.query_params.get('country', None)
        gender = self.request.query_params.get('gender', None)
        role = self.request.query_params.get('role', None)

        # Apply filters based on query parameters
        if status:
            queryset = queryset.filter(account__account_status=status)
        if country:
            queryset = queryset.filter(country__iexact=country)  # Case-insensitive filter
        if gender:
            queryset = queryset.filter(gender=gender)
        if role:
            queryset = queryset.filter(role=role)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"KYC with ID {kwargs['pk']} retrieved successfully.")
            return Response(serializer.data)
        except KYC.DoesNotExist:
            logger.error(f"KYC with id {kwargs['pk']} not found")
            raise NotFound(detail="KYC record not found. Please check the ID.")
        except Exception as e:
            logger.error(f"Error retrieving KYC: {str(e)}")
            return Response({"detail": {str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            # Get the user's KYC record
            user = self.request.user
            instance = KYC.objects.get(user=user)

            # Use the serializer to validate and update the instance
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            logger.info(f"KYC for user {request.user.id} updated successfully.")
            return Response(serializer.data)

        except KYC.DoesNotExist:
            logger.error(f"KYC for user {request.user.id} not found")
            raise NotFound(detail="KYC not found. Please submit your KYC details first.")
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to update their KYC")
            raise PermissionDenied(detail="You do not have permission to update this KYC.")
        except ValidationError as ve:
            logger.error(f"Validation error while updating KYC for user {request.user.id}: {str(ve)}")
            return Response({"detail": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error updating KYC for user {request.user.id}: {str(e)}")
            return Response({"detail": {str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.request.user
            instance = KYC.objects.get(user=user)
            self.perform_destroy(instance)
            logger.info(f"KYC for user {user.id} deleted successfully.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KYC.DoesNotExist:
            logger.error(f"KYC for user {request.user.id} not found")
            raise NotFound(detail="KYC not found. Please submit your KYC details first.")
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to delete their KYC")
            raise PermissionDenied(detail="You do not have permission to delete this KYC.")
        except Exception as e:
            logger.error(f"Unexpected error deleting KYC for user {request.user.id}: {str(e)}")
            return Response({"detail": {str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
