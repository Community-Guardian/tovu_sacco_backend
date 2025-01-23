from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Investment
from .serializers import InvestmentSerializer
import logging

# Set up logging
logger = logging.getLogger(__name__)

class InvestmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing investments for a single Sacco. It includes list, create, retrieve, update, and delete operations.
    """
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]  # Ensures that only authenticated users can access
    queryset = Investment.objects.all()

    def get_queryset(self):
        """
        Get the investments for the specific Sacco.
        """
        return Investment.objects.all()

    def perform_create(self, serializer):
        """
        Override perform_create to add custom logic or logging when an investment is created.
        """
        logger.info(f"Creating a new investment: {serializer.validated_data['name']} for Sacco ")
        serializer.save()

    def perform_update(self, serializer):
        """
        Override perform_update to add custom logic or logging when an investment is updated.
        """
        logger.info(f"Updating investment #{self.kwargs['pk']}: {serializer.validated_data['name']} for Sacco")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Override perform_destroy to add custom logic or logging when an investment is deleted.
        """
        logger.info(f"Deleting investment #{instance.id}: {instance.name} for Sacco ")
        instance.delete()
