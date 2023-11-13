from rest_framework import serializers
from api.models import Destination, Tag


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


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)
