"""Takeoff or landing event model."""

from access_log import AccessLog
from django.db import models


class TakeoffOrLandingEvent(AccessLog):
    """Marker for a UAS takeoff/landing. UAS must interop during that time."""
    # Whether the UAS is now in the air
    uas_in_air = models.BooleanField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode('TakeoffOrLandingEvent (pk%s, user:%s, timestamp:%s, '
                       'uas_in_air:%s)' %
                       (str(self.pk), self.user.__unicode__(),
                        str(self.timestamp), str(self.uas_in_air)))

    @classmethod
    def getFlightPeriodsForUser(cls, user):
        """Gets the time period for which the given user was in flight.

        Args:
            user: The user for which to get flight periods for.
        Returns:
            A list of (flight_start, flight_end) tuples where flight_start is
            the time the flight started and flight_end is the time the flight
            ended.  This is based off the takeoff and landing events stored. A
            flight_X of None indicates since the beginning or until the end of
            time. The list will be sorted by flight_start and the periods will
            be non-intersecting.
        """
        time_periods = list()
        # Get the access logs for the user
        access_logs = TakeoffOrLandingEvent.getAccessLogForUser(user)

        # If UAS in air at start, assume forgot to log takeoff, assign infinity
        if len(access_logs) > 0 and not access_logs[0].uas_in_air:
            time_periods.append((None, access_logs[0].timestamp))

        # Use transition from ground to air and air to ground for flight periods
        takeoff_time = None
        landing_time = None
        uas_in_air = False
        for cur_log in access_logs:
            # Check for transition from ground to air
            if not uas_in_air and cur_log.uas_in_air:
                takeoff_time = cur_log.timestamp
                uas_in_air = cur_log.uas_in_air
            # Check for transition from air to ground
            if uas_in_air and not cur_log.uas_in_air:
                landing_time = cur_log.timestamp
                uas_in_air = cur_log.uas_in_air
                time_periods.append((takeoff_time, landing_time))

        # If UAS in air at end, assume forgot to log landing, assign infinity
        if uas_in_air:
            time_periods.append((access_logs[len(access_logs)-1].timestamp,
                                 None))

        return time_periods
