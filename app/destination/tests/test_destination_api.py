from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Destination
from destination.serializers import DestinationSerializer, \
    DestinationDetailSerializer


DESTINATION_URL = reverse('destination:destination-list')


def detail_url(destination_id):
    """generate destination detail url"""
    return reverse('destination:destination-detail', args=[destination_id])


def create_destination(user, **params):
    """Helper function to create destination"""
    destination_values = {
        'name': 'Test Destination',
        'description': 'Test description',
        'country': 'Test country',
        'city': 'Test city',
        'rating': 4.5,
    }
    # Overwrite the dictionary with any params passed in
    destination_values.update(params)

    return Destination.objects.create(user=user, **destination_values)


def sample_user(**params):
    """Create a sample user"""
    return get_user_model().objects.create_user(
        email='test@example.com',
        password='testpass',
        **params
    )


class PublicDestinationApiTests(TestCase):
    """Test the publicly available destination API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that login is required for retrieving destinations
        res = self.client.get(DESTINATION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDestinationApiTests(TestCase):
    """Test the authorized user destination API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_destinations(self):
        # create multiple destinations
        create_destination(user=self.user)
        create_destination(user=self.user)

        res = self.client.get(DESTINATION_URL)
        destinations = Destination.objects.all().order_by('-id')
        serializer = DestinationSerializer(destinations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check that the response data matches the serializer data
        self.assertEqual(res.data, serializer.data)

    def test_destinations_authenticated_user(self):
        '''Test that destinations are limited to authenticated users'''

        # create a destination for an unauthenticated user
        user2 = get_user_model().objects.create_user(
            'test2@example.com',
            'testpass'
        )
        create_destination(user=user2)
        create_destination(user=self.user)
        res = self.client.get(DESTINATION_URL)

        # check that only the authenticated user's destination is returned
        destinations = Destination.objects.filter(user=self.user)
        serializer = DestinationSerializer(destinations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_destination_detail_view(self):
        '''Test viewing a destination detail'''
        destination = create_destination(user=self.user)
        url = detail_url(destination.id)
        res = self.client.get(url)
        serializer = DestinationDetailSerializer(destination)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_destination(self):
        '''Test creating destination'''
        payload = {
            'name': 'Test Destination',
            'country': 'Test country',
            'city': 'Test city',
            'rating': 4.5,
        }
        res = self.client.post(DESTINATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        destination = Destination.objects.get(id=res.data['id'])
        # compare the payload values to the destination object
        for k, v in payload.items():
            self.assertEqual(v, getattr(destination, k))
        # check destination object was created by the correct user
        self.assertEqual(destination.user, self.user)

    def test_update_destination(self):
        '''Test updating a destination'''
        destination = create_destination(user=self.user)
        payload = {'rating': 5.0}
        url = detail_url(destination.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        destination.refresh_from_db()
        # check the destination object was updated
        self.assertEqual(destination.rating, payload['rating'])
        # check update destination was created by the same user
        self.assertEqual(destination.user, self.user)

    def test_update_full_destination(self):
        '''Test updating a destination with all fields'''
        destination = create_destination(user=self.user)
        payload = {
            'name': 'Updated name',
            'description': 'Updated description',
            'country': 'Updated country',
            'city': 'Updated city',
            'rating': 5.0,
        }
        url = detail_url(destination.id)
        # put method used to update all fields
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # refresh the destination object from the database
        destination.refresh_from_db()
        # check the destination object was updated
        for k, v in payload.items():
            self.assertEqual(v, getattr(destination, k))
        # check update destination was created by the same user
        self.assertEqual(destination.user, self.user)
