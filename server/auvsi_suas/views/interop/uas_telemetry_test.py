"""Tests for the uas_telemetry module."""

import time
import logging
from auvsi_suas.models import UasTelemetry
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class TestPostUasPosition(TestCase):
    """Tests the postUasPosition view."""

    def setUp(self):
        """Sets up the client, server info URL, and user."""
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')
        self.user.save()
        self.client = Client()
        self.loginUrl = reverse('auvsi_suas:login')
        self.uasUrl = reverse('auvsi_suas:uas_telemetry')
        logging.disable(logging.CRITICAL)

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        client = self.client
        uasUrl = self.uasUrl
        response = client.get(uasUrl)
        self.assertEqual(response.status_code, 400)

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        client = self.client
        loginUrl = self.loginUrl
        uasUrl = self.uasUrl

        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        response = client.post(uasUrl)
        self.assertEqual(response.status_code, 400)
        response = client.post(
            uasUrl, {'longitude': 0,
                     'altitude_msl': 0,
                     'uas_heading': 0})
        self.assertEqual(response.status_code, 400)
        response = client.post(
            uasUrl, {'latitude': 0,
                     'altitude_msl': 0,
                     'uas_heading': 0})
        self.assertEqual(response.status_code, 400)
        response = client.post(
            uasUrl, {'latitude': 0,
                     'longitude': 0,
                     'uas_heading': 0})
        self.assertEqual(response.status_code, 400)
        response = client.post(
            uasUrl, {'latitude': 0,
                     'longitude': 0,
                     'altitude_msl': 0})
        self.assertEqual(response.status_code, 400)

    def eval_request_values(self, lat, lon, alt, heading):
        client = self.client
        uasUrl = self.uasUrl
        response = client.post(uasUrl, {
            'latitude': lat,
            'longitude': lon,
            'altitude_msl': alt,
            'uas_heading': heading
        })
        return response.status_code

    def test_invalid_request_values(self):
        """Tests by specifying correct parameters with invalid values."""
        client = self.client
        loginUrl = self.loginUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        TEST_DATA = [
            (-100, 0, 0, 0),
            (100, 0, 0, 0),
            (0, -190, 0, 0),
            (0, 190, 0, 0),
            (0, 0, 0, -10),
            (0, 0, 0, 370)
        ]  # yapf: disable
        for (lat, lon, alt, heading) in TEST_DATA:
            self.assertEqual(400,
                             self.eval_request_values(lat, lon, alt, heading))

    def test_upload_and_store(self):
        """Tests correct upload and storage of data."""
        client = self.client
        loginUrl = self.loginUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        uasUrl = self.uasUrl

        lat = 10
        lon = 20
        alt = 30
        heading = 40
        response = client.post(uasUrl, {
            'latitude': lat,
            'longitude': lon,
            'altitude_msl': alt,
            'uas_heading': heading
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(UasTelemetry.objects.all()), 1)
        obj = UasTelemetry.objects.all()[0]
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.uas_heading, heading)
        self.assertEqual(obj.uas_position.altitude_msl, alt)
        self.assertEqual(obj.uas_position.gps_position.latitude, lat)
        self.assertEqual(obj.uas_position.gps_position.longitude, lon)

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        if not settings.TEST_ENABLE_LOADTEST:
            return

        client = self.client
        loginUrl = self.loginUrl
        uasUrl = self.uasUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        lat = 10
        lon = 20
        alt = 30
        heading = 40
        total_ops = 0
        start_t = time.clock()
        while time.clock() - start_t < settings.TEST_LOADTEST_TIME:
            client.post(uasUrl, {
                'latitude': lat,
                'longiutde': lon,
                'altitude_msl': alt,
                'uas_heading': heading
            })
            total_ops += 1
        end_t = time.clock()
        total_t = end_t - start_t
        op_rate = total_ops / total_t

        print 'UAS Post Rate (%f)' % op_rate
        self.assertGreaterEqual(op_rate,
                                settings.TEST_LOADTEST_INTEROP_MIN_RATE)
