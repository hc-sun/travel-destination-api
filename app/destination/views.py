from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models import Destination, Tag, Feature
from destination import serializers
from drf_spectacular.utils import OpenApiParameter, \
    OpenApiTypes, extend_schema, extend_schema_view


# extend auto-generated schema by drf-spectacular
@extend_schema_view(
    list=extend_schema(
        description="List all destinations",
        parameters=[
            OpenApiParameter(
                name='tags',
                type=OpenApiTypes.STR,
                description='Filter destinations by tags',
            ),
            OpenApiParameter(
                name='features',
                type=OpenApiTypes.STR,
                description='Filter destinations by features',
            ),
        ]
    ),
)
class DestinationViewSet(viewsets.ModelViewSet):
    """Manage destinations in the database"""
    serializer_class = serializers.DestinationDetailSerializer
    # query the database for all destinations
    queryset = Destination.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def id_to_ints(self, qs):
        """Convert comma seperated id from to integer"""
        return [int(str_id) for str_id in qs.split(',')]

    # overwrite the get_queryset method
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # return self.queryset.filter(user=self.request.user).order_by('-id')
        tags = self.request.query_params.get('tags')
        features = self.request.query_params.get('features')
        queryset = self.queryset

        # if tags or features are provided in the query params
        if tags:
            tag_ids = self.id_to_ints(tags)
            '''
            django ORM query syntax
            tags__id__in is used to filter objects
            where the ID of their related 'tag' objects
            is in a provided list of IDs
            '''
            queryset = self.queryset.filter(tags__id__in=tag_ids)
        if features:
            feature_ids = self.id_to_ints(features)
            queryset = self.queryset.filter(features__id__in=feature_ids)

        return (queryset.filter(user=self.request.user)
                        .order_by('-id')
                        .distinct())

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
# extend_schema_view decorator to extend
# auto-generated schema by drf-spectacular
@extend_schema_view(
    list=extend_schema(
        description="List all tags",
        parameters=[
            OpenApiParameter(
                name='is_tag_destination',
                type=OpenApiTypes.INT, enum=[0, 1],
                description='Filter tags that are assigned to a destination',
            ),
        ]
    ),
)
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

        # if is_tag_destination is provided in the query params
        is_tag_destination = bool(int(
            self.request.query_params.get('is_tag_destination', 0)))

        queryset = self.queryset
        # if True, filter tags that are assigned to a destination
        if is_tag_destination:
            queryset = queryset.filter(destination__isnull=False)

        return (queryset.filter(user=self.request.user)
                .order_by('-name')
                .distinct())


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

        is_feature_destination = bool(int(
            self.request.query_params.get('is_feature_destination', 0)))

        queryset = self.queryset
        if is_feature_destination:
            queryset = queryset.filter(destination__isnull=False)

        return (queryset.filter(user=self.request.user)
                .order_by('-name')
                .distinct())
