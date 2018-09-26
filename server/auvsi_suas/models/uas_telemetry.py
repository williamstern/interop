"""UAS Telemetry model."""

import datetime
import itertools
from collections import defaultdict

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from auvsi_suas.models import distance
from auvsi_suas.models import units
from auvsi_suas.models.access_log import AccessLog
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.patches.simplekml_patch import AltitudeMode
from auvsi_suas.patches.simplekml_patch import Color
from auvsi_suas.proto import mission_pb2

# Threshold at which telemetry is too close to (0, 0) and likely noise.
BAD_TELEMETRY_THRESHOLD_DEGREES = 0.1
# The incremental step in seconds for an interpolation of telemetry.
TELEMETRY_INTERPOLATION_STEP = datetime.timedelta(seconds=0.1)
# The max time gap between two telemetry to interpolate between.
TELEMETRY_INTERPOLATION_MAX_GAP = datetime.timedelta(seconds=5.0)


class UasTelemetry(AccessLog):
    """UAS telemetry reported by teams.

    Attributes:
        uas_position: The position of the UAS.
        uas_heading: The (true north) heading of the UAS in degrees.
    """
    uas_position = models.ForeignKey(AerialPosition, on_delete=models.CASCADE)
    uas_heading = models.FloatField()

    def duplicate(self, other):
        """Determines whether this UasTelemetry is equivalent to another.

        This differs from the Django __eq__() method which simply compares
        primary keys. This method compares the field values.

        Args:
            other: The other log for comparison.
        Returns:
            True if they are equal.
        """
        return (self.uas_position.duplicate(other.uas_position) and
                self.uas_heading == other.uas_heading)

    def json(self):
        ret = {
            'id': self.pk,
            'user': self.user.pk,
            'timestamp': self.timestamp.isoformat(),
            'latitude': self.uas_position.gps_position.latitude,
            'longitude': self.uas_position.gps_position.longitude,
            'altitude_msl': self.uas_position.altitude_msl,
            'heading': self.uas_heading,
        }

        return ret

    @classmethod
    def by_user(cls, *args, **kwargs):
        """Gets the time-sorted list of access log for the given user.

        Note: This prefetches the related AerialPosition and GpsPosition
        for each entry.  Thus, any subsequent changes to those entries in
        the database after fetch may not be reflected in the objects.

        Args:
            user: The user to get the access log for.
        Returns:
            A list of access log objects for the given user sorted by timestamp.
        """
        # Almost every user of UasTelemetry.by_user wants to use
        # the related AerialPosition and GpsPosition.  To avoid excessive
        # database queries, we select these values from the database up front.
        return super(UasTelemetry, cls).by_user(*args, **kwargs) \
                .select_related('uas_position__gps_position')

    @classmethod
    def dedupe(cls, logs):
        """Dedupes a set of UAS telemetry logs.

        For every set of sequential telemetry logs that are duplicates, it will
        filter all but the first log. Sensors and autopilots are unlikely to
        provide exactly the same data, even if the system is stationary, so
        logs which have exactly the same values are likely duplicates. Duplicate
        telemetry data is not allowed per the rules, so it is filtered.

        Args:
            logs: A sorted list of UasTelemetry logs.
        Returns:
            A list containing the non-duplicate logs in the original list.
        """
        # Check that logs were provided.
        if not logs:
            return logs

        # For each log, compare to previous. If different, add to output.
        filtered = []
        prev_log = None
        for log in logs:
            if prev_log is None or not prev_log.duplicate(log):
                # New unique log.
                filtered.append(log)
                prev_log = log

        return filtered

    @classmethod
    def filter_bad(cls, logs):
        """Filters bad telemetry from the list.

        Args:
            logs: A sorted list of UasTelemetry logs.
        Returns:
            A list containing the non-bad logs.
        """

        def _is_good(log):
            # Positions near (0,0) are likely GPS/autopilot noise.
            pos = log.uas_position.gps_position
            return max(abs(pos.latitude),
                       abs(pos.longitude)) > BAD_TELEMETRY_THRESHOLD_DEGREES

        return filter(lambda log: _is_good(log), logs)

    @classmethod
    def kml(cls, user, logs, kml, kml_doc):
        """
        Appends kml nodes describing the given user's flight as described
        by the log array given.

        Args:
            user: A Django User to get username from
            logs: A list of UasTelemetry elements
            kml: A simpleKML Container to which the flight data will be added
            kml_doc: The simpleKML Document to which schemas will be added
        Returns:
            None
        """
        # KML Compliant Datetime Formatter
        kml_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        icon = 'http://maps.google.com/mapfiles/kml/shapes/airports.png'

        kml_folder = kml.newfolder(name=user.username)

        flights = TakeoffOrLandingEvent.flights(user)
        if len(flights) == 0:
            return

        logs = UasTelemetry.dedupe(UasTelemetry.filter_bad(logs))
        for i, flight in enumerate(flights):
            label = 'Flight {}'.format(i + 1)  # Flights are one-indexed
            kml_flight = kml_folder.newfolder(name=label)

            flight_logs = filter(lambda x: flight.within(x.timestamp), logs)

            coords = []
            angles = []
            when = []
            for entry in flight_logs:
                pos = entry.uas_position.gps_position
                # Spatial Coordinates
                coord = (pos.longitude, pos.latitude,
                         units.feet_to_meters(entry.uas_position.altitude_msl))
                coords.append(coord)

                # Time Elements
                time = entry.timestamp.strftime(kml_datetime_format)
                when.append(time)

                # Degrees heading, tilt, and roll
                angle = (entry.uas_heading, 0.0, 0.0)
                angles.append(angle)

            # Create a new track in the folder
            trk = kml_flight.newgxtrack(name='Flight Path')
            trk.altitudemode = AltitudeMode.absolute

            # Append flight data
            trk.newwhen(when)
            trk.newgxcoord(coords)
            trk.newgxangle(angles)

            # Set styling
            trk.extrude = 1  # Extend path to ground
            trk.style.linestyle.width = 2
            trk.style.linestyle.color = Color.blue
            trk.iconstyle.icon.href = icon

    @classmethod
    def live_kml(cls, kml, timespan):
        users = User.objects.all()
        for user in users:
            period_logs = UasTelemetry.by_user(user)\
                .filter(timestamp__gt=timezone.now() - timespan)

            if len(period_logs) < 1:
                continue

            linestring = kml.newlinestring(name=user.username)
            coords = []
            for entry in period_logs:
                pos = entry.uas_position.gps_position
                # Spatial Coordinates
                coord = (pos.longitude, pos.latitude,
                         units.feet_to_meters(entry.uas_position.altitude_msl))
                coords.append(coord)
            linestring.coords = coords
            linestring.altitudemode = AltitudeMode.absolute
            linestring.extrude = 1
            linestring.style.linestyle.color = Color.blue
            linestring.style.polystyle.color = Color.changealphaint(
                100, Color.blue)

    @classmethod
    def interpolate(cls,
                    uas_telemetry_logs,
                    step=TELEMETRY_INTERPOLATION_STEP,
                    max_gap=TELEMETRY_INTERPOLATION_MAX_GAP):
        """Interpolates the ordered set of telemetry.

        Args:
            uas_telemetry_logs: The telemetry to interpolate.
            step: The discrete interpolation step in seconds.
            max_gap: The max time between telemetry to interpolate.
        Returns:
            An iterable set of telemetry.
        """
        for ix, log in enumerate(uas_telemetry_logs):
            yield log

            if ix + 1 >= len(uas_telemetry_logs):
                continue
            next_log = uas_telemetry_logs[ix + 1]

            dt = next_log.timestamp - log.timestamp
            if dt > max_gap or dt <= datetime.timedelta(seconds=0):
                continue

            t = log.timestamp + step
            while t < next_log.timestamp:
                n_w = (t - log.timestamp).total_seconds() / dt.total_seconds()
                w = (next_log.timestamp - t
                     ).total_seconds() / dt.total_seconds()
                weighted_avg = lambda v, n_v: w * v + n_w * n_v

                telem = UasTelemetry()
                telem.user = log.user
                telem.timestamp = t
                telem.uas_position = AerialPosition()
                telem.uas_position.gps_position = GpsPosition()
                telem.uas_position.gps_position.latitude = weighted_avg(
                    log.uas_position.gps_position.latitude,
                    next_log.uas_position.gps_position.latitude)
                telem.uas_position.gps_position.longitude = weighted_avg(
                    log.uas_position.gps_position.longitude,
                    next_log.uas_position.gps_position.longitude)
                telem.uas_position.altitude_msl = weighted_avg(
                    log.uas_position.altitude_msl,
                    next_log.uas_position.altitude_msl)
                telem.uas_heading = weighted_avg(log.uas_heading,
                                                 next_log.uas_heading)
                yield telem

                t += step

    @classmethod
    def satisfied_waypoints(cls, home_pos, waypoints, uas_telemetry_logs):
        """Determines whether the UAS satisfied the waypoints.

        Waypoints must be satisfied in order. The entire pattern may be
        restarted at any point. The best (most waypoints satisfied) attempt
        will be returned.

        Assumes that waypoints are at least
        settings.SATISFIED_WAYPOINT_DIST_MAX_FT apart.

        Args:
            home_pos: The home position for projections.
            waypoints: A list of waypoints to check against.
            uas_telemetry_logs: A list of UAS Telemetry logs to evaluate.
        Returns:
            A list of auvsi_suas.proto.WaypointEvaluation.
        """
        # Reduce telemetry from telemetry to waypoint hits.
        # This will make future processing more efficient via data reduction.
        # While iterating, compute the best distance seen for feedback.
        best = {}
        hits = []
        for log in cls.interpolate(uas_telemetry_logs):
            for iw, waypoint in enumerate(waypoints):
                dist = log.uas_position.distance_to(waypoint.position)
                best[iw] = min(best.get(iw, dist), dist)
                score = max(
                    0,
                    float(settings.SATISFIED_WAYPOINT_DIST_MAX_FT - dist) /
                    settings.SATISFIED_WAYPOINT_DIST_MAX_FT)
                if score > 0:
                    hits.append((iw, dist, score))
        # Remove redundant hits which wouldn't be part of best sequence.
        # This will make future processing more efficient via data reduction.
        hits = [
            max(g, key=lambda x: x[2])
            for _, g in itertools.groupby(hits, lambda x: x[0])
        ]

        # Find highest scoring sequence via dynamic programming.
        # Implement recurrence relation:
        #   S(iw, ih) = s[iw, ih] + max_{k=[0,ih)} S(iw-1, k)
        dp = defaultdict(lambda: defaultdict(lambda: (0, None, None)))
        highest_total = None
        highest_total_pos = (None, None)
        for iw in range(len(waypoints)):
            for ih, (hiw, hdist, hscore) in enumerate(hits):
                # Compute score for assigning current hit to current waypoint.
                score = hscore if iw == hiw else 0.0
                # Compute best total score, which includes this match score and
                # best of all which could come before it.
                prev_iw = iw - 1
                total_score = score
                total_score_back = (None, None)
                if prev_iw >= 0:
                    for prev_ih in range(ih + 1):
                        (prev_total_score, _) = dp[prev_iw][prev_ih]
                        new_total_score = prev_total_score + score
                        if new_total_score > total_score:
                            total_score = new_total_score
                            total_score_back = (prev_iw, prev_ih)
                dp[iw][ih] = (total_score, total_score_back)
                # Track highest score seen.
                if highest_total is None or total_score > highest_total:
                    highest_total = total_score
                    highest_total_pos = (iw, ih)
        # Traceback sequence to get scores and distance for score.
        scores = defaultdict(lambda: (0, None))
        cur_pos = highest_total_pos
        while cur_pos != (None, None):
            cur_iw, cur_ih = cur_pos
            hiw, hdist, hscore = hits[cur_ih]
            if cur_iw == hiw:
                scores[cur_iw] = (hscore, hdist)
            _, cur_pos = dp[cur_iw][cur_ih]

        # Convert to evaluation.
        waypoint_evals = []
        for iw, waypoint in enumerate(waypoints):
            score, dist = scores[iw]
            waypoint_eval = mission_pb2.WaypointEvaluation()
            waypoint_eval.id = iw
            waypoint_eval.score_ratio = score
            if dist is not None:
                waypoint_eval.closest_for_scored_approach_ft = dist
            if iw in best:
                waypoint_eval.closest_for_mission_ft = best[iw]
            waypoint_evals.append(waypoint_eval)
        return waypoint_evals


@admin.register(UasTelemetry)
class UasTelemetryModelAdmin(admin.ModelAdmin):
    show_full_result_count = False
    raw_id_fields = ("uas_position", )
    list_display = ('user', 'timestamp', 'uas_position', 'uas_heading')
