"""Mission Clock event model."""

import logging
from auvsi_suas.models.access_log import AccessLog
from auvsi_suas.models.time_period import TimePeriod
from django.contrib import admin
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class MissionClockEvent(AccessLog):
    """Marker for a team going on/off mission clock.

    Attributes:
        team_on_clock: Whether the team is now on the mission clock.
        team_on_timeout: Whether the team is now in a timeout.
    """
    team_on_clock = models.BooleanField()
    team_on_timeout = models.BooleanField()

    @classmethod
    def user_on_clock(cls, user, time=None):
        """Determine if given user is currently on mission clock.

        Args:
            user: User to get mission clock status.
            time: Time to check status for, default now.
        Returns:
            True if the user currently on clock, False otherwise.
        """
        event = cls.last_for_user(user, end_time=time)
        return event.team_on_clock if event else False

    @classmethod
    def user_on_timeout(cls, user, time=None):
        """Determine if given user is currently on timeout.

        Args:
            user: User to get timeout status.
            time: Time to check status for, default now.
        Returns:
            True if user is on timeout, False otherwise.
        """
        event = cls.last_for_user(user, end_time=time)
        return event.team_on_timeout if event else False

    @classmethod
    def missions(cls, user):
        """Gets the time periods which represents periods on the mission clock.

        Args:
            user: The user for which to get mission periods for.
        Returns:
            A list of TimePeriod objects for the mission clock.
        """
        return TimePeriod.from_events(
            MissionClockEvent.by_user(user),
            is_start_func=lambda x: x.team_on_clock,
            is_end_func=lambda x: not x.team_on_clock)


@admin.register(MissionClockEvent)
class MissionClockEventModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'team_on_clock', 'team_on_timeout')
