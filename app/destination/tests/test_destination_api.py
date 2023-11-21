from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Destination, Tag, Feature
from destination.serializers import DestinationSerializer, \
    DestinationDetailSerializer
import tempfile
import os
from PIL import Image


DESTINATION_URL = reverse('destination:destination-list')


def detail_url(destination_id):
    """generate destination detail url"""
    return reverse('destination:destination-detail', args=[destination_id])

def image_url(destination_id):
    """generate destination image url"""
    return reverse('destination:destination-upload-image', args=[destination_id])

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

    def test_delete_destination(self):
        '''Test deleting a destination'''
        destination = create_destination(user=self.user)
        url = detail_url(destination.id)
        # delete method used to delete a destination
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # check the destination object was deleted
        object_exists = Destination.objects.filter(id=destination.id).exists()
        self.assertFalse(object_exists)
        self.assertEqual(destination.user, self.user)

    def test_create_destination_tag(self):
        '''Test creating a destination with tags'''
        payload = {
            'name': 'Test Destination',
            'country': 'Test country',
            'city': 'Test city',
            'rating': 4.5,
            'tags': [{'name': 'Tag 1'}, {'name': 'Tag 2'}]
        }
        res = self.client.post(DESTINATION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        destinations = Destination.objects.filter(user=self.user)
        self.assertEqual(destinations.count(), 1)
        destination = destinations[0]
        self.assertEqual(destination.tags.count(), 2)
        self.assertEqual(destination.tags.all()[0].name, 'Tag 1')
        self.assertEqual(destination.tags.all()[1].name, 'Tag 2')

    def test_create_destination_no_duplicate_tag(self):
        '''Test creating a destination with existing tags'''
        # create a tag with a name
        tag = Tag.objects.create(user=self.user, name='Tag 1')
        # create a destination that contains same tag name
        payload = {
            'name': 'Test Destination',
            'country': 'Test country',
            'city': 'Test city',
            'rating': 4.5,
            'tags': [{'name': 'Tag 1'}, {'name': 'Tag 2'}]
        }
        res = self.client.post(DESTINATION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        destinations = Destination.objects.filter(user=self.user)
        # check that only one destination was created by this user
        self.assertEqual(destinations.count(), 1)

        destination = destinations[0]
        # check there are 2 tags associated with the destination
        self.assertEqual(destination.tags.count(), 2)

        # check the tag name is the same as the tag created above
        self.assertEqual(destination.tags.all()[0].name, tag.name)
        self.assertEqual(destination.tags.all()[1].name, 'Tag 2')

    def test_update_destination_tag(self):
        ''''Test updating a destination with tags'''
        destination = create_destination(user=self.user)
        payload = {
            'tags': [{'name': 'Tag 1'}, {'name': 'Tag 2'}]
        }
        url = detail_url(destination.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        destination.refresh_from_db()
        tags = destination.tags.all()
        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[0].name, 'Tag 1')
        self.assertEqual(tags[1].name, 'Tag 2')

    def test_update_replace_destination_tag(self):
        '''Test updating a destination with tags'''
        destination = create_destination(user=self.user)
        # create a tag with a name
        tag = Tag.objects.create(user=self.user, name='Tag 1')
        # add the tag to the destination
        destination.tags.add(tag)
        payload = {
            'tags': [{'name': 'Tag 2'}]
        }
        url = detail_url(destination.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        destination.refresh_from_db()
        tags = destination.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].name, 'Tag 2')

    def test_update_remove_destination_tags(self):
        '''Test removing tags from a destination'''
        destination = create_destination(user=self.user)
        # create a tag with a name
        tag = Tag.objects.create(user=self.user, name='Tag 1')
        # add the tag to the destination
        destination.tags.add(tag)
        payload = {
            'tags': []
        }
        url = detail_url(destination.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        destination.refresh_from_db()
        tags = destination.tags.all()
        self.assertEqual(len(tags), 0)

    def test_create_destination_feature(self):
        '''Test creating a destination with features'''
        payload = {
            'name': 'Test Destination',
            'country': 'Test country',
            'city': 'Test city',
            'rating': 4.5,
            'features': [{'name': 'Feature 1'}, {'name': 'Feature 2'}]
        }
        res = self.client.post(DESTINATION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        destinations = Destination.objects.filter(user=self.user)
        self.assertEqual(destinations.count(), 1)
        destination = destinations[0]
        self.assertEqual(destination.features.count(), 2)
        self.assertEqual(destination.features.all()[0].name, 'Feature 1')
        self.assertEqual(destination.features.all()[1].name, 'Feature 2')

    def test_create_destination_no_duplicate_feature(self):
        '''Test creating a destination with existing features'''

        # create a feature with a name
        feature = Feature.objects.create(user=self.user, name='Feature 1')

        # create a destination that contains same feature name
        payload = {
            'name': 'Test Destination',
            'country': 'Test country',
            'city': 'Test city',
            'rating': 4.5,
            'features': [{'name': 'Feature 1'}, {'name': 'Feature 2'}]
        }
        res = self.client.post(DESTINATION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        destinations = Destination.objects.filter(user=self.user)
        # check that only one destination was created by this user
        self.assertEqual(destinations.count(), 1)

        destination = destinations[0]
        # check there are only 2 features created
        self.assertEqual(destination.features.count(), 2)

        # check the feature name is the same as the feature created above
        self.assertEqual(destination.features.all()[0].name, feature.name)
        self.assertEqual(destination.features.all()[1].name, 'Feature 2')

    def test_update_destination_feature(self):
        '''Test updating a destination with features'''
        destination = create_destination(user=self.user)
        payload = {
            'features': [{'name': 'Feature 1'},]
        }
        url = detail_url(destination.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        destination.refresh_from_db()
        features = destination.features.all()
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0].name, 'Feature 1')

    def test_update_replace_destination_feature(self):
        '''Test updating a destination with features'''
        # create a destination
        destination = create_destination(user=self.user)
        # create a feature with a name
        feature = Feature.objects.create(user=self.user, name='Feature 1')
        # add the feature to the destination
        destination.features.add(feature)

        # create a new feature
        payload = {
            'features': [{'name': 'Feature 2'}]
        }
        url = detail_url(destination.id)
        # only update the new feature
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        destination.refresh_from_db()
        features = destination.features.all()
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0].name, 'Feature 2')

    def test_update_remove_destination_features(self):
        '''Test removing features from a destination'''

        destination = create_destination(user=self.user)
        feature = Feature.objects.create(user=self.user, name='Feature 1')
        destination.features.add(feature)

        # update the feature with an empty list
        payload = {
            'features': []
        }
        url = detail_url(destination.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        destination.refresh_from_db()
        features = destination.features.all()
        self.assertEqual(len(features), 0)


class ImageTests(TestCase):
    '''Test uploading an image to a destination'''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass',
        )
        self.client.force_authenticate(self.user)
        self.destination = create_destination(user=self.user)

    # delete the test image after each test
    def tearDown(self):
        self.destination.image.delete()

    def test_upload_image_to_destination(self):
        '''Test uploading an image to a destination'''
        url = image_url(self.destination.id)
        # create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # create a 10x10 pixel image
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            # move the file pointer back to the start of the file
            # to avoid uploading an empty file
            ntf.seek(0)
            # upload the image file to the destination
            res = self.client.post(url, {'image': ntf}, format='multipart')
        self.destination.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check the destination object has an image associated with it
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.destination.image.path))

    def test_upload_invalid_image(self):
        '''Test uploading an invalid image'''
        url = image_url(self.destination.id)
        # create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w+b') as ntf:
            ntf.write(b"This is an invalid image file.")
            ntf.seek(0)
            # upload the text file to the destination
            res = self.client.post(url, {'image': ntf}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
