from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models import Destination
from destination import serializers


class DestinationViewSet(viewsets.ModelViewSet):
    """Manage destinations in the database"""
    serializer_class = serializers.DestinationDetailSerializer
    # query the database for all destinations
    queryset = Destination.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # overwrite the get_queryset method
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return serializers.DestinationSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new destination"""
        serializer.save(user=self.request.user)
