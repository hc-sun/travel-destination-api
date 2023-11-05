from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    '''Converts the user object to JSON'''

    class Meta:
        model = get_user_model()
        # fields to include in the serializer
        fields = ('email', 'password', 'name')
        # extra settings for the fields
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        # use the create_user function from the UserManager class
        return get_user_model().objects.create_user(**validated_data)
