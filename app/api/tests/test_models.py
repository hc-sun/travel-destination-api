from django.test import TestCase
from django.contrib.auth import get_user_model
from api import models


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_email(self):
        """Test the email for a new user is normalized"""
        email = "test@Example.COM"
        user = get_user_model().objects.create_user(email=email)
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a new user with no email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None)

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="admin123"
        )

        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.check_password("admin123"))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_destination(self):
        '''Test creating a destination'''
        uesr = get_user_model().objects.create_user(
            email="test@example.com",
            password="test123"
        )
        destination = models.Destination.objects.create(
            user=uesr,
            name="test",
            description="test description",
            country="test country",
            city="test city",
            rating=4.5
        )
        self.assertEqual(destination.name, "test")

    def test_create_tag(self):
        '''Test creating a tag'''
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test123"
        )
        tag = models.Tag.objects.create(user=user, name="tag")
        self.assertEqual(tag.name, str(tag))

    def test_create_feature(self):
        '''Test creating a feature'''
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test123"
        )
        feature = models.Feature.objects.create(user=user, name="feature")
        self.assertEqual(feature.name, str(feature))
