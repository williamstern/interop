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

    def test_user_on_clock(self):
        """Tests the user_on_clock method."""
        log = MissionClockEvent(user=self.user1,
                                team_on_clock=False,
                                team_on_timeout=False)
        log.save()
        log = MissionClockEvent(user=self.user2,
                                team_on_clock=True,
                                team_on_timeout=False)
        log.save()

        self.assertFalse(MissionClockEvent.user_on_clock(self.user1))
        self.assertTrue(MissionClockEvent.user_on_clock(self.user2))

    def test_user_on_timeout(self):
        """Tests the user_on_timeout method."""
        log = MissionClockEvent(user=self.user1,
                                team_on_clock=False,
                                team_on_timeout=False)
        log.save()
        log = MissionClockEvent(user=self.user2,
                                team_on_clock=False,
                                team_on_timeout=True)
        log.save()

        self.assertFalse(MissionClockEvent.user_on_timeout(self.user1))
        self.assertTrue(MissionClockEvent.user_on_timeout(self.user2))
