from django.contrib.auth import get_user_model
from django.test import TestCase
from api.models import Tag, Destination
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from destination.serializers import TagSerializer


TAG_URL = reverse('destination:tag-list')


def detail_url(tag_id):
    """Given a tag id, return the detail url"""
    return reverse('destination:tag-detail', args=[tag_id])


class PublicTagApiTests(TestCase):
    """Test the publicly available tag API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that login is required for retrieving tags
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test the authorized user tag API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass'
            )
        self.client.force_authenticate(self.user)

    def test_get_tags(self):
        """Test getting tags"""
        Tag.objects.create(user=self.user, name='Test tag')
        Tag.objects.create(user=self.user, name='Test tag2')
        res = self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by('-name')
        # many=True serializing a list of objects
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_authenticated_user(self):
        """Test that tags returned are for the authenticated user"""

        user2 = get_user_model().objects.create_user(
            email='test2@example.com',
            password='testpass'
            )
        Tag.objects.create(user=user2, name='Test tag2')

        tag = Tag.objects.create(user=self.user, name='Test tag')
        res = self.client.get(TAG_URL)

        # user2 is not authenticated
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name='Test tag')
        payload = {'name': 'New tag name'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(res.data['name'], tag.name)

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name='Test tag')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # check that the tag is deleted
        tags = Tag.objects.all()
        self.assertEqual(len(tags), 0)

    def test_filter_only_tags_associated_with_destinations(self):
        """Test that only tags associated with destinations are returned"""
        tag1 = Tag.objects.create(user=self.user, name='Test tag1')
        tag2 = Tag.objects.create(user=self.user, name='Test tag2')
        destination = Destination.objects.create(
            user=self.user,
            name='Test destination',
            description='Test description',
            country='Test country',
            city='Test city',
            rating=4.5,
            )

        # only add tag1 to the destination
        destination.tags.add(tag1)

        res = self.client.get(TAG_URL, {'is_tag_destination': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_no_duplicate_tags(self):
        """Test that no duplicate tags are returned"""
        # create two tags
        tag1 = Tag.objects.create(user=self.user, name='Test tag1')
        Tag.objects.create(user=self.user, name='Test tag2')

        destination1 = Destination.objects.create(
            user=self.user,
            name='Test destination1',
            description='Test description',
            country='Test country',
            city='Test city',
            rating=4.5,
            )
        destination2 = Destination.objects.create(
            user=self.user,
            name='Test destination2',
            description='Test description',
            country='Test country',
            city='Test city',
            rating=2.0,
            )

        # add tag1 to both destinations
        destination1.tags.add(tag1)
        destination2.tags.add(tag1)

        res = self.client.get(TAG_URL, {'is_tag_destination': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
