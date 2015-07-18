"""Model for an access log."""

import datetime
import numpy as np
from time_period import TimePeriod
from django.conf import settings
from django.db import models
from django.utils import timezone


class AccessLog(models.Model):
    """Base class which logs access of information."""
    # Timestamp of the access
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    # The user which accessed the data
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("%s (pk:%s, user:%s, timestamp:%s)" %
                       (self.__class__.__name__, str(self.pk),
                        self.user.__unicode__(), str(self.timestamp)))

    @classmethod
    def by_user(cls, user):
        """Gets the time-sorted list of access log for the given user.

        Args:
            user: The user to get the access log for.
        Returns:
            A list of access log objects for the given user sorted by timestamp.
        """
        return cls.objects.filter(user_id=user.pk).order_by('timestamp')

    @classmethod
    def user_active(cls, user, base=None, delta=None):
        """Determines if a user is 'active'.

        A user is 'active' if they have reported telemetry since delta
        time in the past.

        Args:
            user: User to determine if is active
            base: Base time for active period, defaults to now
            delta: time period before base to consider user active
        Returns:
            True if user reported telemetry since base - delta
        """
        if base is None:
            base = timezone.now()
        if delta is None:
            delta = datetime.timedelta(seconds=10)

        since = base - delta

        return 0 != cls.by_user(user) \
            .filter(timestamp__gt=since) \
            .filter(timestamp__lt=base).count()

    @classmethod
    def by_time_period(cls, user, time_periods):
        """Gets a list of time-sorted lists of access logs for each time period.

        The method returns the full sets of AccessLogs for each TimePeriod. If
        overlapping TimePeriods are provided, the results may contain duplicate
        logs.

        Args:
            user: The user to get the access log for.
            time_periods: A list of TimePeriod objects.
        Returns:
            A list of AccessLog lists, where each AccessLog list contains all
            AccessLogs corresponding to the related TimePeriod.
        """
        ret = []

        for period in time_periods:
            logs = cls.by_user(user)

            if period.start:
                logs = logs.filter(timestamp__gte=period.start)
            if period.end:
                logs = logs.filter(timestamp__lte=period.end)

            ret.append(logs)

        return ret

    @classmethod
    def getAccessLogRates(cls, time_periods, time_period_access_logs):
        """Gets the access log rates.

        Args:
            time_periods: A list of (time_start, time_end) tuples sorted by
                time_start indicating time periods of interest where None
                indicates infinity.
            time_period_access_logs: A list of access log lists for each time
                period.
        Returns:
            A (max, avg) tuple. The max is the max time between logs, and avg
            is the avg time between logs.
            """
        # FIXME(prattmic): truly take TimePeriod here
        if len(time_periods) > 0 and type(time_periods[0]) == TimePeriod:
            time_periods = [(t.start, t.end) for t in time_periods]

        times_between_logs = list()
        for time_period_id in range(len(time_periods)):
            # Get the times and logs for this period
            (time_start, time_end) = time_periods[time_period_id]
            cur_access_logs = time_period_access_logs[time_period_id]

            # Account for a time period with no logs
            if len(cur_access_logs) == 0:
                if time_start is not None and time_end is not None:
                    time_diff = (time_end - time_start).total_seconds()
                    times_between_logs.append(time_diff)
                continue

            # Account for time between takeoff and first log
            if time_start is not None:
                first_log = cur_access_logs[0]
                time_diff = (first_log.timestamp - time_start).total_seconds()
                times_between_logs.append(time_diff)
            # Account for time between logs
            for access_log_id in range(len(cur_access_logs) - 1):
                log_t = cur_access_logs[access_log_id]
                log_tp1 = cur_access_logs[access_log_id + 1]
                time_diff = (log_tp1.timestamp - log_t.timestamp
                             ).total_seconds()
                times_between_logs.append(time_diff)
            # Account for time between last log and landing
            if time_end is not None:
                last_log = cur_access_logs[len(cur_access_logs) - 1]
                time_diff = (time_end - last_log.timestamp).total_seconds()
                times_between_logs.append(time_diff)

        # Compute log rates
        if times_between_logs:
            times_between_logs = np.array(times_between_logs)
            times_between_max = np.max(times_between_logs)
            times_between_avg = np.mean(times_between_logs)
            return (times_between_max, times_between_avg)
        else:
            return (None, None, None)
