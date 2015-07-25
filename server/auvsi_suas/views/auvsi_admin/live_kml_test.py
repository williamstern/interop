"""Tests for the live_kml module."""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
import logging


class TestGenerateLiveKMLCommon(TestCase):
    """Tests the generateKML view."""

    def setUp(self):
        """Sets up the tests."""
        # Create nonadmin user
        self.nonadmin_user = User.objects.create_user(
            'testuser', 'testemail@x.com', 'testpass')
        self.nonadmin_user.save()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            'testuser2', 'testemail@x.com', 'testpass')
        self.admin_user.save()

        # Create URLs for testing
        self.login_url = reverse('auvsi_suas:login')
        self.eval_url = reverse('auvsi_suas:live_kml')
        self.update_url = reverse('auvsi_suas:update_kml')
        logging.disable(logging.CRITICAL)


class TestGenerateLiveKMLNoFixture(TestGenerateLiveKMLCommon):
    def test_generate_live_kml_not_logged_in(self):
        """Tests the generate KML method."""
        response = self.client.get(self.eval_url)
        self.assertGreaterEqual(response.status_code, 300)

    def test_generate_live_kml(self):
        """Tests the generate KML method."""
        self.client.post(self.login_url,
                         {'username': 'testuser2',
                          'password': 'testpass'})
        response = self.client.get(self.eval_url)
        self.assertEqual(response.status_code, 200)

    def test_generate_live_kml_nonadmin(self):
        """Tests the generate KML method."""
        self.client.post(self.login_url,
                         {'username': 'testuser',
                          'password': 'testpass'})
        response = self.client.get(self.eval_url)
        self.assertGreaterEqual(response.status_code, 300)

    def test_generate_live_kml_update_no_session_id(self):
        """Tests the generate KML method."""
        response = self.client.get(self.update_url)
        self.assertGreaterEqual(response.status_code, 300)

    def test_generate_live_kml_update_bad_session_id(self):
        """Tests the generate KML method."""
        bad_id = '360l8fjqnvzbviy590gmjeltma9fx26f'
        response = self.client.get(self.update_url, {'sessionid': bad_id})
        self.assertGreaterEqual(response.status_code, 403)

    def test_generate_live_kml_update_nonadmin(self):
        """Tests the generate KML method."""
        response = self.client.post(
            self.login_url, {'username': 'testuser',
                             'password': 'testpass'})
        response = self.client.get(
            self.update_url, {'sessionid': self.get_session_id(response)})
        self.assertGreaterEqual(response.status_code, 300)

    def test_generate_live_kml_update(self):
        """Tests the generate KML method."""
        response = self.client.post(
            self.login_url, {'username': 'testuser2',
                             'password': 'testpass'})
        response = self.client.get(
            self.update_url, {'sessionid': self.get_session_id(response)})
        self.assertEqual(response.status_code, 200)

    @staticmethod
    def get_session_id(response):
        for item in response.client.cookies.items():
            morsel = item[1]
            if morsel.key == 'sessionid':
                return morsel.value


class TestGenerateLiveKMLWithFixture(TestGenerateLiveKMLCommon):
    """Tests the generateKML view."""
    fixtures = ['testdata/sample_mission.json']

    def test_generate_live_kml(self):
        """Tests the generate KML method."""
        self.client.post(self.login_url,
                         {'username': 'testuser2',
                          'password': 'testpass'})
        response = self.client.get(self.eval_url)
        self.assertEqual(response.status_code, 200)
