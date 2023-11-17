from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Feature
from api.serializers import FeatureSerializer


FEATURES_URL = reverse('destination:feature-list')


class PublicFeatureApiTests(TestCase):
    """Test the publicly available features API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving features"""
        res = self.client.get(FEATURES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFeatureApiTests(TestCase):
    """Test the authorized user features API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_features(self):
        """Test getting features"""
        Feature.objects.create(user=self.user, name='Test feature')
        Feature.objects.create(user=self.user, name='Test feature2')

        res = self.client.get(FEATURES_URL)
        features = Feature.objects.all().order_by('-name')
        serializer = FeatureSerializer(features, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_features_authenticated_user(self):
        """Test that features returned are for the authenticated user"""

        # create a feature for the authenticated user
        feature = Feature.objects.create(user=self.user, name='Test feature')

        # create a new user with a new feature
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass',
        )
        Feature.objects.create(user=user2, name='Test feature2')

        res = self.client.get(FEATURES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check that only the feature for the authenticated user is returned
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], feature.id)
        self.assertEqual(res.data[0]['name'], feature.name)
