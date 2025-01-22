import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
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
            return Response(serializer.data)
        except Account.DoesNotExist:
            logger.error(f"Account with id {kwargs['pk']} not found")
            raise NotFound(detail="Account not found")
        except Exception as e:
            logger.error(f"Error retrieving account: {str(e)}")
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Account.DoesNotExist:
            logger.error(f"Account with id {kwargs['pk']} not found")
            raise NotFound(detail="Account not found")
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to update account {kwargs['pk']}")
            raise PermissionDenied(detail="You do not have permission to update this account")
        except Exception as e:
            logger.error(f"Error updating account: {str(e)}")
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Account.DoesNotExist:
            logger.error(f"Account with id {kwargs['pk']} not found")
            raise NotFound(detail="Account not found")
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to delete account {kwargs['pk']}")
            raise PermissionDenied(detail="You do not have permission to delete this account")
        except Exception as e:
            logger.error(f"Error deleting account: {str(e)}")
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KYCViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing KYC instances.
    """
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Limit access to only the user's KYC unless admin
        user = self.request.user
        if user.is_staff:
            return KYC.objects.all()
        return KYC.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except KYC.DoesNotExist:
            logger.error(f"KYC with id {kwargs['pk']} not found")
            raise NotFound(detail="KYC not found")
        except Exception as e:
            logger.error(f"Error retrieving KYC: {str(e)}")
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except KYC.DoesNotExist:
            logger.error(f"KYC with id {kwargs['pk']} not found")
            raise NotFound(detail="KYC not found")
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to update KYC {kwargs['pk']}")
            raise PermissionDenied(detail="You do not have permission to update this KYC")
        except Exception as e:
            logger.error(f"Error updating KYC: {str(e)}")
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KYC.DoesNotExist:
            logger.error(f"KYC with id {kwargs['pk']} not found")
            raise NotFound(detail="KYC not found")
        except PermissionDenied:
            logger.warning(f"Permission denied for user {request.user.id} to delete KYC {kwargs['pk']}")
            raise PermissionDenied(detail="You do not have permission to delete this KYC")
        except Exception as e:
            logger.error(f"Error deleting KYC: {str(e)}")
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)