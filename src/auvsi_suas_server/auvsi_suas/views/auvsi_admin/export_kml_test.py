"""Tests for the evaluate_teams module."""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
import logging
from xml.etree import ElementTree


class TestGenerateKML(TestCase):
    """Tests the generateKML view."""
    def __init__(self, *args, **kwargs):
        super(TestGenerateKML, self).__init__(*args, **kwargs)
        self.folders = ['Teams', 'Mission']
        self.users = ['testuser']
        self.coordinates = ['0.0, 0.0, 0.0']

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
        self.loginUrl = reverse('auvsi_suas:login')
        self.evalUrl = reverse('auvsi_suas:export_data')
        logging.disable(logging.CRITICAL)

    def test_generateKML_nonadmin(self):
        """Tests the generate KML method."""
        self.client.post(self.loginUrl, {'username': 'testuser', 'password': 'testpass'})
        response = self.client.get(self.evalUrl)
        self.assertGreaterEqual(response.status_code, 300)

    def test_generateKML(self):
        """Tests the generate KML method."""
        self.client.post(self.loginUrl, {'username': 'testuser2', 'password': 'testpass'})
        response = self.client.get(self.evalUrl)
        self.assertEqual(response.status_code, 200)

        kml_data = response.content
        self.validate_kml(kml_data, self.folders, self.users, self.coordinates)

    def validate_kml(self, kml_data, folders, users, coordinates):
        ElementTree.fromstring(kml_data)
        for folder in folders:
            tag = '<name>{}</name>'.format(folder)
            self.assertTrue(tag in kml_data)

        for user in users:
            tag = '<name>{}</name>'.format(user)
            self.assertTrue(tag in kml_data)

        for coord in coordinates:
            self.assertTrue(coord in kml_data)


class TestGenerateKMLWithFixture(TestGenerateKML):
    """Tests the generateKML view."""
    fixtures = ['testdata/sample_mission.json']

    def __init__(self, *args, **kwargs):
        super(TestGenerateKMLWithFixture, self).__init__(*args, **kwargs)
        self.folders = ['Teams', 'Mission']
        self.users = ['testuser', 'user0', 'user1']
        self.coordinates = [
            '-76.0,38.0,0.0',
            '-76.0,38.0,10.0',
            '-76.0,38.0,20.0',
            '-76.0,38.0,30.0',
            '-76.0,38.0,100.0',
            '-76.0,38.0,30.0',
            '-76.0,38.0,60.0',
            '0.0, 0.0, 0.0',
        ]

