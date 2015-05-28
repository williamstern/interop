"""Tests for the uas_telemetry module."""

from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import UasTelemetry
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone


class TestUasTelemetry(TestCase):
    """Tests the UasTelemetry model."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        pos = GpsPosition(latitude=100, longitude=200)
        pos.save()
        apos = AerialPosition(gps_position=pos, altitude_msl=200)
        apos.save()
        user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        log = UasTelemetry(
                timestamp=timezone.now(), user=user, uas_position=apos,
                uas_heading=100)
        log.save()
        self.assertTrue(log.__unicode__())
