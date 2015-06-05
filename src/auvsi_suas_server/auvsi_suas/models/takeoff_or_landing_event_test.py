"""Tests for the takeoff_or_landing_event module."""

import datetime
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.models.access_log_test import TestAccessLogCommon
from django.utils import timezone


class TestTakeoffOrLandingEventModel(TestAccessLogCommon):
    """Tests the TakeoffOrLandingEvent model."""

    def setUp(self):
        super(TestTakeoffOrLandingEventModel, self).setUp()

        self.ten_minutes = datetime.timedelta(minutes=10)

    def create_event(self, time, uas_in_air):
        """Create a TakeoffOrLandingEvent for test user."""
        event = TakeoffOrLandingEvent(user=self.user1,
                                      uas_in_air=uas_in_air)
        event.save()
        event.timestamp = time
        event.save()
        return event

    def evaluate_periods(self, expected):
        """Check actual periods against expected."""
        periods = TakeoffOrLandingEvent.getFlightPeriodsForUser(self.user1)

        self.assertSequenceEqual(expected, periods)

    def test_unicode(self):
        """Tests the unicode method executes."""
        log = TakeoffOrLandingEvent(user=self.user1, uas_in_air=True)
        log.save()
        log.__unicode__()

    def test_basic_flight_period(self):
        """Single flight reported as period."""
        self.create_event(self.year2000, True)
        self.create_event(self.year2000 + self.ten_minutes, False)

        self.evaluate_periods([
            (self.year2000, self.year2000 + self.ten_minutes),
        ])

    def test_flight_period_missing_takeoff(self):
        """Missing takeoff reported as None."""
        self.create_event(self.year2000, False)

        self.evaluate_periods([
            (None, self.year2000),
        ])

    def test_flight_period_missing_landing(self):
        """Missing landing reported as None."""
        self.create_event(self.year2000, True)

        self.evaluate_periods([
            (self.year2000, None),
        ])

    def test_flight_period_multiple_flights(self):
        """Multiple flight reported together."""
        self.create_event(self.year2000, True)
        self.create_event(self.year2000 + self.ten_minutes, False)

        self.create_event(self.year2001, True)
        self.create_event(self.year2001 + self.ten_minutes, False)

        self.evaluate_periods([
            (self.year2000, self.year2000 + self.ten_minutes),
            (self.year2001, self.year2001 + self.ten_minutes),
        ])

    def test_flight_period_multiple_flights_order(self):
        """Multiple flights listed in chronological order."""
        self.create_event(self.year2001, True)
        self.create_event(self.year2001 + self.ten_minutes, False)

        self.create_event(self.year2000, True)
        self.create_event(self.year2000 + self.ten_minutes, False)

        self.evaluate_periods([
            (self.year2000, self.year2000 + self.ten_minutes),
            (self.year2001, self.year2001 + self.ten_minutes),
        ])

    def test_flight_period_missing_multiple(self):
        """Multiple flight can be missing details."""
        # Forgot takeoff
        self.create_event(self.year2000, False)

        # Normal
        self.create_event(self.year2001, True)
        self.create_event(self.year2001 + self.ten_minutes, False)

        # Forgot landing
        self.create_event(self.year2002, True)

        self.evaluate_periods([
            (None, self.year2000),
            (self.year2001, self.year2001 + self.ten_minutes),
            (self.year2002, None),
        ])

    def test_flight_period_multiple_landing(self):
        """Double landing ignored"""
        self.create_event(self.year2000, True)
        self.create_event(self.year2000 + self.ten_minutes, False)

        # Land again? Ignored
        self.create_event(self.year2000 + 2*self.ten_minutes, False)

        self.create_event(self.year2001, True)
        self.create_event(self.year2001 + self.ten_minutes, False)

        self.evaluate_periods([
            (self.year2000, self.year2000 + self.ten_minutes),
            (self.year2001, self.year2001 + self.ten_minutes),
        ])

    def test_flight_period_multiple_takeoff(self):
        """Double takeoff ignored."""
        self.create_event(self.year2000, True)
        # Take off again? Ignored
        self.create_event(self.year2000 + self.ten_minutes, True)
        # Land
        self.create_event(self.year2000 + 2*self.ten_minutes, False)

        self.create_event(self.year2001, True)
        self.create_event(self.year2001 + self.ten_minutes, False)

        self.evaluate_periods([
            (self.year2000, self.year2000 + 2*self.ten_minutes),
            (self.year2001, self.year2001 + self.ten_minutes),
        ])
