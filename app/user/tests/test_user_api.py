from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
UPDATE_USER_URL = reverse('user:update')



def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        # make sure password is not returned in the response
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'pwd',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # make sure user is not created
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        # make sure token is returned in the response
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created if invalid credentials are given"""
        create_user(
            email='test@exmaple.com',
            password='testpass',
            name='Test Name'
        )
        payload = {
            'email': 'test@example.com',
            'password': 'wrongpass',
            'name': 'Test Name'
        }
        res = self.client.post(TOKEN_URL, payload)
        # make sure token is not returned in the response
        self.assertNotIn('token', res.data)
        # compare status code
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.post(UPDATE_USER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test User API (authenticated)"""

    def setUp(self):
        self.user = create_user(
            email = 'test@example.com',
            password = 'testpass',
            name = 'Test Name'
        )
        self.client = APIClient()
        # force authentication
        self.client.force_authenticate(user=self.user)

    def test_get_profile_success(self):
        """Test get profile for logged in user"""
        res = self.client.get(UPDATE_USER_URL)
        # compare status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # compare response data
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_update_user_not_allowed(self):
        """Test that POST is not allowed on the update user url"""
        res = self.client.post(UPDATE_USER_URL, {})
        # compare status code post is not allowed
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_update_user(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            'name': 'New Name',
            'password': 'newpassword123'
        }
        res = self.client.patch(UPDATE_USER_URL, payload)
        # refresh the user object
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
