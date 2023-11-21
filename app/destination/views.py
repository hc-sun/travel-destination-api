from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models import Destination, Tag, Feature
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
        elif self.action == 'upload_image':
            return serializers.DestinationImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new destination"""
        serializer.save(user=self.request.user)

    # @action decorator to create custom upload image action
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a destination"""
        destination = self.get_object()
        serializer = self.get_serializer(
            destination,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# viewsets.GenericViewSet allows to use the mixins
# which allows GET and PATCH
class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,):
    """Manage tags in the database"""
    serializer_class = serializers.TagSerializer
    # query the database for all tags
    queryset = Tag.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # overwrite the get_queryset method
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class FeatureViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,):
    """Manage features in the database"""
    serializer_class = serializers.FeatureSerializer

    # query the database for all features
    queryset = Feature.objects.all()

    authentication_classes = (TokenAuthentication,)
    # user must be authenticated to use this API endpoint
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
