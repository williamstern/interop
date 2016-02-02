"""Tests for the mission_clock_event module."""

import datetime
from auvsi_suas.models import MissionClockEvent
from auvsi_suas.models.access_log_test import TestAccessLogCommon
from django.utils import timezone


class TestMissionClockEventModel(TestAccessLogCommon):
    """Tests the MissionClockEvent model."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        log = MissionClockEvent(user=self.user1,
                                team_on_clock=True,
                                team_on_timeout=False)
        log.save()
        self.assertIsNotNone(log.__unicode__())
