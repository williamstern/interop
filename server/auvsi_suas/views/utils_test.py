"""Tests for the utils module."""

import json
from auvsi_suas.proto import interop_admin_api_pb2
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from google.protobuf import json_format

gps_conversion_url = reverse('auvsi_suas:gps_conversion')


class TestGpsConversion(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', 'email@example.com', 'superpass')
        self.superuser.save()

    def test_not_authenticated(self):
        """Tests that not authenticated return 403."""
        response = self.client.post(gps_conversion_url)
        self.assertEqual(403, response.status_code)

    def test_not_admin(self):
        """Tests that not admin return 403."""
        user = User.objects.create_user('user', 'email@example.com',
                                             'testpass')
        user.save()
        self.client.force_login(user)

        response = self.client.post(gps_conversion_url)
        self.assertEqual(403, response.status_code)

    def test_invalid_request(self):
        """Tests that invalid requests return 400."""
        self.client.force_login(self.superuser)

        response = self.client.post(gps_conversion_url)
        self.assertEqual(400, response.status_code)

        request_proto = interop_admin_api_pb2.GpsConversionRequest()
        request_proto.latitude = 'ABC'
        request_proto.longitude = 'DEF'

        response = self.client.post(
                gps_conversion_url,
                json_format.MessageToJson(request_proto),
                content_type='application/json')
        self.assertEqual(400, response.status_code)


    def test_conversion(self):
        """Tests that it can convert a valid request."""
        self.client.force_login(self.superuser)

        request_proto = interop_admin_api_pb2.GpsConversionRequest()
        request_proto.latitude = 'N38-08-46.57'
        request_proto.longitude = 'W076-25-41.39'

        response = self.client.post(
                gps_conversion_url,
                json_format.MessageToJson(request_proto),
                content_type='application/json')
        self.assertEqual(200, response.status_code)

        response_proto = interop_admin_api_pb2.GpsConversionResponse()
        json_format.Parse(response.content, response_proto)
        self.assertAlmostEqual(response_proto.latitude, 38.146269, places=5)
        self.assertAlmostEqual(response_proto.longitude, -76.428164, places=5)
