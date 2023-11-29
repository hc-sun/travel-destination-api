from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


HEALTH_CHECK_URL = reverse('health-check')


class HealthCheckTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        """Test health check endpoint"""
        res = self.client.get(HEALTH_CHECK_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'status': 'ok'})
