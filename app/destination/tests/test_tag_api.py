from django.contrib.auth import get_user_model
from django.test import TestCase
from api.models import Tag
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
