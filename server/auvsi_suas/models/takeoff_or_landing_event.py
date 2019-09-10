"""Takeoff or landing event model."""

import logging
from auvsi_suas.models.access_log import AccessLogMixin
from auvsi_suas.models.mission_config import MissionConfig
from auvsi_suas.models.time_period import TimePeriod
from django.contrib import admin
from django.db import models

logger = logging.getLogger(__name__)


class TakeoffOrLandingEvent(AccessLogMixin):
    """Marker for a UAS takeoff/landing. UAS must interop during that time."""

    # The mission for which this is an event.
    mission = models.ForeignKey(MissionConfig, on_delete=models.CASCADE)
    # Whether the UAS is now in the air.
    uas_in_air = models.BooleanField()

    class Meta:
        index_together = AccessLogMixin.Meta.index_together + (
            ('mission', 'user', 'timestamp'), )

    @classmethod
    def flights(cls, mission, user):
        """Gets the time periods for which the given user was in flight.

        Args:
            mission: The mission for which to get flights.
            user: The user for which to get flight periods for.
        Returns:
            A list of TimePeriod objects corresponding to individual flights.
        """
        return TimePeriod.from_events(
            TakeoffOrLandingEvent.by_user(user).filter(mission_id=mission.pk),
            is_start_func=lambda x: x.uas_in_air,
            is_end_func=lambda x: not x.uas_in_air)

    @classmethod
    def user_in_air(cls, user, time=None):
        """Determine if given user is currently in-air

        Args:
            user: User to get in-flight status for
            time: Time to check in-air status; default now
        Returns:
            True if user is currently in-flight, False otherwise
        """
        event = cls.last_for_user(user, end_time=time)
        if event:
            return event.uas_in_air
        return False


@admin.register(TakeoffOrLandingEvent)
class TakeoffOrLandingEventModelAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('pk', 'timestamp', 'user', 'mission', 'uas_in_air')
