"""Tests for the uas_telemetry module."""

import iso8601
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import UasTelemetry
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from simplekml import Kml


class TestUasTelemetry(TestCase):
    """Tests the UasTelemetry model."""

    def setUp(self):
        user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        user.save()

        pos = GpsPosition(latitude=10, longitude=100)
        pos.save()

        apos = AerialPosition(gps_position=pos, altitude_msl=200)
        apos.save()

        self.log = UasTelemetry(
                timestamp=timezone.now(), user=user, uas_position=apos,
                uas_heading=90)
        self.log.save()

    def test_unicode(self):
        """Tests the unicode method executes."""
        self.assertTrue(self.log.__unicode__())

    def test_toJSON(self):
        """Tests JSON-style output."""
        data = self.log.toJSON()

        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('timestamp', data)
        self.assertIn('latitude', data)
        self.assertIn('longitude', data)
        self.assertIn('altitude_msl', data)
        self.assertIn('heading', data)

        # Timestamp is valid ISO 8601, with timezone
        iso8601.parse_date(data['timestamp'])

        self.assertEqual(10, data['latitude'])
        self.assertEqual(100, data['longitude'])
        self.assertEqual(200, data['altitude_msl'])
        self.assertEqual(90, data['heading'])


class TestUasTelemetryKML(TestCase):
    # String formatter for KML format that expects lon, lat, alt arguments
    coord_format = '<gx:coord>{} {} {}</gx:coord>'

    def test_kml_simple(self):
        # Create User
        nonadmin_user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        nonadmin_user.save()

        coordinates = [
            (-76.0, 38.0, 0.0),
            (-76.0, 38.0, 10.0),
            (-76.0, 38.0, 20.0),
            (-76.0, 38.0, 30.0),
            (-76.0, 38.0, 100.0),
            (-76.0, 38.0, 30.0),
            (-76.0, 38.0, 60.0),
        ]
        # Create Coordinates
        for coord in coordinates:
            self.create_log_element(*coord, user=nonadmin_user)

        kml = Kml()
        UasTelemetry.kml(
            user=nonadmin_user,
            logs=UasTelemetry.getAccessLogForUser(nonadmin_user),
            kml=kml,
        )
        for coord in coordinates:
            tag = self.coord_format.format(coord[1], coord[0], coord[2])
            self.assertTrue(tag in kml.kml())

    def test_kml_empty(self):
        # Create User
        nonadmin_user = User.objects.create_user(
                'testuser2', 'testemail@x.com', 'testpass')
        nonadmin_user.save()

        kml = Kml()
        UasTelemetry.kml(
            user=nonadmin_user,
            logs=UasTelemetry.getAccessLogForUser(nonadmin_user),
            kml=kml,
        )

    def test_kml_filter(self):
        # Create User
        nonadmin_user = User.objects.create_user(
                'testuser3', 'testemail@x.com', 'testpass')
        nonadmin_user.save()

        coordinates = [
            (-76.0, 38.0, 0.0),
            (-76.0, 38.0, 10.0),
            (-76.0, 38.0, 20.0),
            (-76.0, 38.0, 30.0),
            (-76.0, 38.0, 100.0),
            (-76.0, 38.0, 30.0),
            (-76.0, 38.0, 60.0),
        ]
        filtered_out = [
            (0.1, 0.001, 100),
            (0.0, 0.0, 0)
        ]
        # Create Coordinates
        for coord in coordinates:
            self.create_log_element(*coord, user=nonadmin_user)
        for coord in filtered_out:
            self.create_log_element(*coord, user=nonadmin_user)

        kml = Kml()
        UasTelemetry.kml(
            user=nonadmin_user,
            logs=UasTelemetry.getAccessLogForUser(nonadmin_user),
            kml=kml,
        )

        for filtered in filtered_out:
            tag = self.coord_format.format(filtered[1], filtered[0], filtered[2])
            self.assertTrue(tag not in kml.kml())

        for coord in coordinates:
            tag = self.coord_format.format(coord[1], coord[0], coord[2])
            self.assertTrue(tag in kml.kml())

    def create_log_element(self, lat, lon, alt, user):
        pos = GpsPosition(latitude=lat, longitude=lon)
        pos.save()
        apos = AerialPosition(gps_position=pos, altitude_msl=alt)
        apos.save()
        log = UasTelemetry(
            timestamp=timezone.now(),
            user=user,
            uas_position=apos,
            uas_heading=100,
        )
        log.save()
