from rest_framework import serializers
from api.models import Destination, Tag, Feature


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class FeatureSerializer(serializers.ModelSerializer):
    """Serializer for feature objects"""

    class Meta:
        model = Feature
        fields = ('id', 'name')
        read_only_fields = ('id',)


class DestinationSerializer(serializers.ModelSerializer):
    """Serializer for destination objects"""

    tags = TagSerializer(many=True, required=False)
    features = FeatureSerializer(many=True, required=False)

    class Meta:
        model = Destination
        fields = (
            'id',
            'name',
            'country',
            'city',
            'rating',
            'tags',
            'features',
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        """Create and return a new destination"""

        auth_user = self.context['request'].user

        '''
        need to pop tags and features from validated_data first,
        because cannot create a destination with
        direct assignment to a many-to-many field
        '''
        tags = validated_data.pop('tags', [])
        features = validated_data.pop('features', [])
        destination = Destination.objects.create(**validated_data)

        for tag in tags:
            # get_or_create will create a new tag if it doesn't exist
            tag_obj, created = Tag.objects.get_or_create(
                # assign the tag to the authenticated user
                user=auth_user,
                name=tag['name']
                )
            destination.tags.add(tag_obj)

        for feature in features:
            feature_obj, created = Feature.objects.get_or_create(
                user=auth_user,
                name=feature['name']
                )
            destination.features.add(feature_obj)

        return destination

    # instance: existing destination object
    # validated_data: new data to update the destination object
    def update(self, instance, validated_data):
        """Update and return an existing destination"""
        tags = validated_data.pop('tags', [])
        features = validated_data.pop('features', [])

        # if tags is not None
        # means there are new tags provided in the validated_data
        if tags is not None:
            # remove old tags
            instance.tags.clear()
            for tag in tags:
                tag_obj, created = Tag.objects.get_or_create(
                    user=self.context['request'].user,
                    name=tag['name']
                )
                instance.tags.add(tag_obj)

        if features is not None:
            instance.features.clear()
            for feature in features:
                feature_obj, created = Feature.objects.get_or_create(
                    user=self.context['request'].user,
                    name=feature['name']
                )
                instance.features.add(feature_obj)

        # update the other fields
        for key, value in validated_data.items():
            # set attribute of instance to value
            setattr(instance, key, value)

        instance.save()
        return instance


class DestinationDetailSerializer(DestinationSerializer):
    """Serializer for destination detail objects"""
    class Meta(DestinationSerializer.Meta):
        fields = DestinationSerializer.Meta.fields + ('description',)


class DestinationImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to destinations"""

    class Meta:
        model = Destination
        fields = ('id', 'image')
        read_only_fields = ('id',)
        extra_kwargs = {
            'image': {
                'required': True
            }
        }
