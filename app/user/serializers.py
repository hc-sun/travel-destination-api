from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


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

    def update(self, instance, validated_data):
        """
        Overwrite the default update method,
        set the password correctly and return it
        """
        # get and remove the password from the validated data
        password = validated_data.pop('password', None)
        # call the update method of the ModelSerializer class
        user = super().update(instance, validated_data)
        # if the user provided a password, set it
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    '''Serializer for the user authentication object'''
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        '''Validate and authenticate the user'''
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs
