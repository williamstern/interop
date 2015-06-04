"""Tests for the teams module."""

import json
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.models import UasTelemetry
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone


login_url = reverse('auvsi_suas:login')
teams_url = reverse('auvsi_suas:teams')


class TestTeamsViewLoggedOut(TestCase):

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(teams_url)
        self.assertGreaterEqual(response.status_code, 300)

class TestTeamsView(TestCase):
    """Tests the teams view."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
                'superuser', 'email@example.com', 'superpass')
        self.superuser.save()

        # Login
        response = self.client.post(login_url, {
            'username': 'superuser',
            'password': 'superpass'
        })
        self.assertEqual(200, response.status_code)

    def create_data(self):
        """Create a basic sample dataset."""
        self.user1 = User.objects.create_user(
                'user1', 'email@example.com', 'testpass')
        self.user1.save()

        self.user2 = User.objects.create_user(
                'user2', 'email@example.com', 'testpass')
        self.user2.save()

        # user1 is flying
        event = TakeoffOrLandingEvent(user=self.user1, uas_in_air=True)
        event.save()

        # user2 has landed
        event = TakeoffOrLandingEvent(user=self.user2, uas_in_air=True)
        event.save()
        event = TakeoffOrLandingEvent(user=self.user2, uas_in_air=False)
        event.save()

        # user2 is active
        self.timestamp = timezone.now()

        gps = GpsPosition(latitude=38.6462, longitude=-76.2452)
        gps.save()

        pos = AerialPosition(gps_position=gps, altitude_msl=0)
        pos.save()

        telem = UasTelemetry(user=self.user2, uas_position=pos,
                             uas_heading=90)
        telem.save()
        telem.timestamp = self.timestamp
        telem.save()

    def test_normal_user(self):
        """Normal users not allowed access."""
        user = User.objects.create_user(
                'testuser', 'email@example.com', 'testpass')
        user.save()

        # Login
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(200, response.status_code)

        response = self.client.get(teams_url)
        self.assertGreaterEqual(response.status_code, 300)

    def test_no_users(self):
        """No users results in empty list, no superusers."""
        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        self.assertEqual([], json.loads(response.content))

    def test_post(self):
        """POST not allowed"""
        response = self.client.post(teams_url)
        self.assertEqual(400, response.status_code)

    def test_correct_json(self):
        """Response JSON is properly formatted."""
        self.create_data()

        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(2, len(data))

        for user in data:
            self.assertIn('id', user)
            self.assertIn('name', user)
            self.assertIn('in_air', user)
            self.assertIn('active', user)

    def test_users_correct(self):
        """User names and status correct."""
        self.create_data()

        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual('user1', data[0]['name'])
        self.assertEqual(True, data[0]['in_air'])
        self.assertEqual(False, data[0]['active'])

        self.assertEqual('user2', data[1]['name'])
        self.assertEqual(False, data[1]['in_air'])
        self.assertEqual(True, data[1]['active'])
