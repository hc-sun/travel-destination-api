from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Feature, Destination
from destination.serializers import FeatureSerializer


FEATURES_URL = reverse('destination:feature-list')


def detail_url(feature_id):
    """Return feature detail URL"""
    return reverse('destination:feature-detail', args=[feature_id])


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

    def test_update_feature(self):
        """Test updating a feature"""
        feature = Feature.objects.create(user=self.user, name='Test feature')
        payload = {'name': 'New feature name'}
        url = detail_url(feature.id)
        res = self.client.patch(url, payload)
        feature.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(feature.name, payload['name'])

    def test_delete_feature(self):
        """Test deleting a feature"""
        feature = Feature.objects.create(user=self.user, name='Test feature')
        url = detail_url(feature.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Feature.objects.count(), 0)

    def test_filter_only_features_associated_with_destinations(self):
        """Test that only features associated with destinations are returned"""
        feature1 = Feature.objects.create(user=self.user, name='Test feature1')
        feature2 = Feature.objects.create(user=self.user, name='Test feature2')
        destination = Destination.objects.create(
            user=self.user,
            name='Test destination',
            country='Test country',
            city='Test city',
            rating=4.5,
        )

        # only add feature1 to the destination
        destination.features.add(feature1)

        res = self.client.get(FEATURES_URL, {'is_feature_destination': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = FeatureSerializer(feature1)
        serializer2 = FeatureSerializer(feature2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_no_duplicate_features(self):
        """Test that no duplicated features are returned"""
        # create two features
        feature1 = Feature.objects.create(user=self.user, name='Test feature1')
        Feature.objects.create(user=self.user, name='Test feature2')

        destination1 = Destination.objects.create(
            user=self.user,
            name='Test destination1',
            country='Test country',
            city='Test city',
            rating=4.5,
        )
        destination2 = Destination.objects.create(
            user=self.user,
            name='Test destination2',
            country='Test country',
            city='Test city',
            rating=4.5,
        )

        # add feature1 to both destinations
        destination1.features.add(feature1)
        destination2.features.add(feature1)

        res = self.client.get(FEATURES_URL, {'is_feature_destination': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
