from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminSiteTests(TestCase):
    '''
    Test Django admin site
    '''

    def setUp(self):
        '''
        Setup function which runs before every test
        It creates a test client and test users
        '''
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="admin123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="user123",
            name="Test user full name"
        )

    def test_users_listed(self):
        '''
        Test that users are listed on user page
        '''
        url = reverse("admin:api_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        '''
        Test that the user edit page works
        '''
        url = reverse("admin:api_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
