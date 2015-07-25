"""Tests for the login module."""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class TestLoginUserView(TestCase):
    """Tests the login_user view."""

    def setUp(self):
        """Sets up the test by creating a test user."""
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')
        self.user.save()
        self.client = Client()
        self.login_url = reverse('auvsi_suas:login')

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        client = self.client
        login_url = self.login_url

        # Test GET instead of POST, without parameters
        response = client.get(login_url)
        self.assertEqual(response.status_code, 400)

        # Test GET instrad of POST, with proper parameters
        response = client.get(
            login_url, {'username': 'testuser',
                        'password': 'testpass'})
        self.assertEqual(response.status_code, 400)

        # Test POST with no parameters
        response = client.post(login_url)
        self.assertEqual(response.status_code, 400)

        # Test POST with a missing parameter
        response = client.post(login_url, {'username': 'test'})
        self.assertEqual(response.status_code, 400)
        response = client.post(login_url, {'password': 'test'})
        self.assertEqual(response.status_code, 400)

    def test_invalid_credentials(self):
        """Tests invalid credentials for login."""
        client = self.client
        login_url = self.login_url
        response = client.post(login_url, {'username': 'a', 'password': 'b'})
        self.assertEqual(response.status_code, 400)

    def test_correct_credentials(self):
        """Tests correct credentials for login."""
        client = self.client
        login_url = self.login_url
        response = client.post(
            login_url, {'username': 'testuser',
                        'password': 'testpass'})
        self.assertEqual(response.status_code, 200)
