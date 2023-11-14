from rest_framework import serializers
from api.models import Destination, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class DestinationSerializer(serializers.ModelSerializer):
    """Serializer for destination objects"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Destination
        fields = (
            'id',
            'name',
            'country',
            'city',
            'rating',
            'tags',
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        """Create and return a new destination"""
        # need to remove tags from validated_data first
        # since it's not in the destination model
        tags = validated_data.pop('tags', [])

        destination = Destination.objects.create(**validated_data)
        auth_user = self.context['request'].user

        for tag in tags:
            # get_or_create will create a new tag if it doesn't exist
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                name=tag['name']
                )
            destination.tags.add(tag_obj)

        return destination


class DestinationDetailSerializer(DestinationSerializer):
    """Serializer for destination detail objects"""
    class Meta(DestinationSerializer.Meta):
        fields = DestinationSerializer.Meta.fields + ('description',)
