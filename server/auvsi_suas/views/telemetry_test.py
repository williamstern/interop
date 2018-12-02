"""Tests for the telemetry module."""

import datetime
import iso8601
import json
import time
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.uas_telemetry import UasTelemetry
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

telemetry_url = reverse('auvsi_suas:telemetry')


class TestTelemetryViewLoggedOut(TestCase):
    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.post(telemetry_url)
        self.assertEqual(403, response.status_code)


class TestTelemetryPost(TestCase):
    """Tests the Telemetry view POST."""

    def setUp(self):
        """Sets up the client, server info URL, and user."""
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')
        self.user.save()
        self.client.force_login(self.user)

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        response = self.client.post(telemetry_url)
        self.assertEqual(400, response.status_code)

        response = self.client.post(telemetry_url, {
            'longitude': 0,
            'altitude_msl': 0,
            'uas_heading': 0,
        })
        self.assertEqual(400, response.status_code)

        response = self.client.post(telemetry_url, {
            'latitude': 0,
            'altitude_msl': 0,
            'uas_heading': 0,
        })
        self.assertEqual(400, response.status_code)

        response = self.client.post(telemetry_url, {
            'latitude': 0,
            'longitude': 0,
            'uas_heading': 0,
        })
        self.assertEqual(400, response.status_code)

        response = self.client.post(telemetry_url, {
            'latitude': 0,
            'longitude': 0,
            'altitude_msl': 0,
        })
        self.assertEqual(400, response.status_code)

    def eval_request_values(self, lat, lon, alt, heading):
        response = self.client.post(telemetry_url, {
            'latitude': lat,
            'longitude': lon,
            'altitude_msl': alt,
            'uas_heading': heading
        })
        return response.status_code

    def test_invalid_request_values(self):
        """Tests by specifying correct parameters with invalid values."""
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
        lat = 10
        lon = 20
        alt = 30
        heading = 40
        response = self.client.post(telemetry_url, {
            'latitude': lat,
            'longitude': lon,
            'altitude_msl': alt,
            'uas_heading': heading
        })
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(UasTelemetry.objects.all()), 1)
        obj = UasTelemetry.objects.all()[0]
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.uas_heading, heading)
        self.assertEqual(obj.uas_position.altitude_msl, alt)
        self.assertEqual(obj.uas_position.gps_position.latitude, lat)
        self.assertEqual(obj.uas_position.gps_position.longitude, lon)

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        lat = 10
        lon = 20
        alt = 30
        heading = 40

        total_ops = 1000
        start_t = time.clock()
        for _ in range(total_ops):
            self.client.post(telemetry_url, {
                'latitude': lat,
                'longiutde': lon,
                'altitude_msl': alt,
                'uas_heading': heading
            })
        end_t = time.clock()
        op_rate = total_ops / (end_t - start_t)
        self.assertGreaterEqual(op_rate, 20)
