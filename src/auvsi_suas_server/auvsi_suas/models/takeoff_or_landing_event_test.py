"""Tests for the takeoff_or_landing_event module."""

import datetime
from auvsi_suas.models import TakeoffOrLandingEvent
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone


# [(user, [(timestamp, in_air)], [(time_start, time_end)]]
TESTDATA_TAKEOFFORLANDINGEVENT = [
    ('no_logs',
        [],
        []),
    ('forgot_takeoff',
        [(0.0, False)],
        [(None, 0.0)]),
    ('forgot_landing',
        [(0.0, True)],
        [(0.0, None)]),
    ('single_flight',
        [(0.0, True), (100.0, False)],
        [(0.0, 100.0)]),
    ('multi_flight',
        [(0.0, True), (100.0, False), (150.0, True), (200.0, False)],
        [(0.0, 100.0), (150.0, 200.0)]),
    ('multi_with_double_forget',
        [(0.0, False), (1.0, True), (2.0, False), (3.0, True)],
        [(None, 0.0), (1.0, 2.0), (3.0, None)]),
    ('missing_inbetween_log',
        [(0.0, True), (1.0, False), (2.0, False), (3.0, True), (4.0, False)],
        [(0.0, 1.0), (3.0, 4.0)]),
]


class TestTakeoffOrLandingEventModel(TestCase):
    """Tests the TakeoffOrLandingEvent model."""

    def setUp(self):
        """Sets up the tests."""
        self.users = list()
        self.user_flight_periods = dict()
        self.base_time = timezone.now().replace(
                hour=0, minute=0, second=0, microsecond=0)
        for (username, logs, periods) in TESTDATA_TAKEOFFORLANDINGEVENT:
            # Create user
            user = User.objects.create_user(
                username, 'testemail@x.com', 'testpass')
            user.save()
            # Create log events
            for (time_offset, uas_in_air) in logs:
                timestamp = self.base_time + datetime.timedelta(
                        seconds = time_offset)
                event = TakeoffOrLandingEvent(
                        user=user, timestamp=timestamp, uas_in_air=uas_in_air)
                event.save()
            # Create expected time periods
            user_periods = self.user_flight_periods.setdefault(user, list())
            for (time_start, time_end) in periods:
                if time_start is not None:
                    time_start = self.base_time + datetime.timedelta(
                            seconds = time_start)
                if time_end is not None:
                    time_end = self.base_time + datetime.timedelta(
                            seconds = time_end)
                user_periods.append((time_start, time_end))

    def test_unicode(self):
        """Tests the unicode method executes."""
        user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        log = TakeoffOrLandingEvent(
                timestamp=timezone.now(), user=user, uas_in_air=True)
        log.save()
        self.assertTrue(log.__unicode__())

    def test_getFlightPeriodsForUser(self):
        """Tests the flight period list class method."""
        for user in self.users:
            event_cls = takeoff_or_landing_event.TakeoffOrLandingEvent
            flight_periods = event_cls.getFlightPeriodsForUser(user)
            exp_periods = self.user_flight_periods[user]
            self.assertEqual(len(flight_periods), len(exp_periods))
            for period_id in range(len(flight_periods)):
                (period_start, period_end) = flight_periods[period_id]
                (exp_start, exp_end) = exp_periods[period_id]
                self.assertAlmostEqual(period_start, exp_start)
                self.assertAlmostEqual(period_end, exp_end)
