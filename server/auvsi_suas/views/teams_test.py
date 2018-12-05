"""Tests for the teams module."""

import dateutil.parser
import functools
import json
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.models.uas_telemetry import UasTelemetry
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

teams_url = reverse('auvsi_suas:teams')
team_url = functools.partial(reverse, 'auvsi_suas:team')


class TestTeamsViewLoggedOut(TestCase):
    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(teams_url)
        self.assertEqual(403, response.status_code)


class TestTeamsView(TestCase):
    """Tests the teams view."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', 'email@example.com', 'superpass')
        self.superuser.save()
        self.client.force_login(self.superuser)

    def create_data(self):
        """Create a basic sample dataset."""
        self.user1 = User.objects.create_user('user1', 'email@example.com',
                                              'testpass')
        self.user1.save()

        self.user2 = User.objects.create_user('user2', 'email@example.com',
                                              'testpass')
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

        self.telem = UasTelemetry(
            user=self.user2, uas_position=pos, uas_heading=90)
        self.telem.save()
        self.telem.timestamp = dateutil.parser.parse(
            u'2016-10-01T00:00:00.0+00:00')

        self.telem.save()

    def test_normal_user(self):
        """Normal users not allowed access."""
        user = User.objects.create_user('testuser', 'email@example.com',
                                        'testpass')
        user.save()
        self.client.force_login(user)

        response = self.client.get(teams_url)
        self.assertEqual(403, response.status_code)

    def test_no_users(self):
        """No users results in empty list, no superusers."""
        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        self.assertEqual([], json.loads(response.content))

    def test_post(self):
        """POST not allowed"""
        response = self.client.post(teams_url)
        self.assertEqual(405, response.status_code)

    def test_correct_json(self):
        """Response JSON is properly formatted."""
        self.create_data()

        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(2, len(data))

        for user in data:
            self.assertIn('team', user)
            self.assertIn('inAir', user)
            if 'telemetry' in user:
                self.assertIn('telemetryTimestamp', user)

    def test_users_correct(self):
        """User names and status correct."""
        self.create_data()

        response = self.client.get(teams_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        names = [d['team'] for d in data]
        self.assertIn('user1', names)
        self.assertIn('user2', names)

        user1 = data[names.index('user1')]
        self.assertEqual(True, user1['inAir'])
        self.assertNotIn('telemetry', user1)

        user2 = data[names.index('user2')]
        self.assertEqual(False, user2['inAir'])
        self.assertEqual({
            u'latitude': 38.6462,
            u'longitude': -76.2452,
            u'altitude': 0.0,
            u'heading': 90.0,
        }, user2['telemetry'])
        self.assertEqual(user2['telemetryTimestamp'],
                         u'2016-10-01T00:00:00+00:00')


class TestTeamViewLoggedOut(TestCase):
    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(team_url(args=[1]))
        self.assertEqual(403, response.status_code)


class TestTeamView(TestCase):
    """Tests the teams-by-id view."""

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'email@example.com',
                                              'testpass')
        self.user1.save()

        self.superuser = User.objects.create_superuser(
            'superuser', 'email@example.com', 'superpass')
        self.superuser.save()
        self.client.force_login(self.superuser)

    def test_bad_id(self):
        """Invalid user id rejected"""
        response = self.client.get(team_url(args=[999]))
        self.assertGreaterEqual(400, response.status_code)

    def test_correct_user(self):
        """User requested is correct"""
        response = self.client.get(team_url(args=[self.user1.username]))
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)
        self.assertIn('team', data)
        self.assertEqual('user1', data['team'])
        self.assertIn('inAir', data)
        self.assertEqual(False, data['inAir'])
        self.assertNotIn('telemetry', data)

    def test_bad_json(self):
        """Invalid json rejected"""
        response = self.client.put(
            team_url(args=[self.user1.username]), 'Hi there!')
        self.assertGreaterEqual(400, response.status_code)

    def test_invalid_in_air(self):
        """invalid in_air rejected"""
        data = json.dumps({
            'team': self.user1.username,
            'active': False,
            'inAir': 'Hi!',
        })

        response = self.client.put(team_url(args=[self.user1.username]), data)
        self.assertGreaterEqual(400, response.status_code)

    def test_no_extra_events(self):
        """No new TakeoffOrLandingEvents created if status doesn't change"""
        data = json.dumps({
            'team': self.user1.username,
            'inAir': False,
        })

        response = self.client.put(team_url(args=[self.user1.username]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(0, TakeoffOrLandingEvent.objects.count())

    def test_update_in_air(self):
        """In-air can be updated"""
        data = json.dumps({
            'team': self.user1.username,
            'inAir': True,
        })

        response = self.client.put(team_url(args=[self.user1.username]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(True, data['inAir'])

        # Event created
        event = TakeoffOrLandingEvent.objects.get()
        self.assertEqual(self.user1, event.user)
        self.assertEqual(True, event.uas_in_air)

    def test_name_ignored(self):
        """name field ignored"""
        expected = self.user1.username

        data = json.dumps({
            'team': 'Hello World!',
            'inAir': False,
        })

        response = self.client.put(team_url(args=[self.user1.username]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(expected, data['team'])

    def test_telemetry_ignored(self):
        """telemetry field ignored"""
        data = json.dumps({
            'team': self.user1.username,
            'telemetry': {
                'latitude': 1
            },
            'inAir': False,
        })

        response = self.client.put(team_url(args=[self.user1.username]), data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertNotIn('telemetry', data)
