from rest_framework import serializers
from api.models import Destination


class DestinationSerializer(serializers.ModelSerializer):
    """Serializer for destination objects"""

    class Meta:
        model = Destination
        fields = (
            'id',
            'name',
            'country',
            'city',
            'rating',
        )
        read_only_fields = ('id',)


class DestinationDetailSerializer(DestinationSerializer):
    """Serializer for destination detail objects"""
    class Meta(DestinationSerializer.Meta):
        fields = DestinationSerializer.Meta.fields + ('description',)
