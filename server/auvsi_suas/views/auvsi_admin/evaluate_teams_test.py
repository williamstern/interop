"""Tests for the evaluate_teams module."""

import logging
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class TestEvaluateTeams(TestCase):
    """Tests the evaluateTeams view."""

    fixtures = ['testdata/sample_mission.json']

    def setUp(self):
        """Sets up the tests."""
        # Create nonadmin user
        self.nonadmin_user = User.objects.create_user(
            'testuser', 'testemail@x.com', 'testpass')
        self.nonadmin_user.save()
        self.nonadmin_client = Client()
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            'testuser2', 'testemail@x.com', 'testpass')
        self.admin_user.save()
        self.admin_client = Client()
        # Create URLs for testing
        self.loginUrl = reverse('auvsi_suas:login')
        self.evalUrl = reverse('auvsi_suas:evaluate_teams')
        logging.disable(logging.CRITICAL)

    def test_evaluateTeams_nonadmin(self):
        """Tests that you can only access data as admin."""
        client = self.client
        loginUrl = self.loginUrl
        evalUrl = self.evalUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        response = client.get(evalUrl)
        self.assertGreaterEqual(response.status_code, 300)

    def test_evaluateTeams(self):
        """Tests the CSV method."""
        client = self.client
        loginUrl = self.loginUrl
        evalUrl = self.evalUrl
        client.post(loginUrl,
                    {'username': 'testuser2',
                     'password': 'testpass'})
        response = client.get(evalUrl)
        self.assertEqual(response.status_code, 200)
        csv_data = response.content
        # Check correct number of rows
        self.assertEqual(len(csv_data.split('\n')), 5)
        # Check some headers
        self.assertTrue('username' in csv_data)
        self.assertTrue('interop_times.server_info.min' in csv_data)
        # Check username fields
        self.assertTrue('user0' in csv_data)
        self.assertTrue('user1' in csv_data)
