"""UAS Telemetry model."""

from access_log import AccessLog
from aerial_position import AerialPosition
from takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.models.moving_obstacle import MovingObstacle
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from auvsi_suas.patches.simplekml_patch import AltitudeMode
from auvsi_suas.patches.simplekml_patch import Color


class UasTelemetry(AccessLog):
    """UAS telemetry reported by teams."""
    # The position of the UAS
    uas_position = models.ForeignKey(AerialPosition)
    # The heading of the UAS in degrees (e.g. 0=north, 90=east)
    uas_heading = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("UasTelemetry (pk:%s, user:%s, timestamp:%s, "
                       "heading:%s, pos:%s)" %
                       (str(self.pk), self.user.__unicode__(),
                        str(self.timestamp), str(self.uas_heading),
                        self.uas_position.__unicode__()))

    def toJSON(self):
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
        threshold = 1  # Degrees

        kml_folder = kml.newfolder(name=user.username)

        periods = TakeoffOrLandingEvent.getFlightPeriodsForUser(user)
        if len(periods) == 0:
            return

        logs = filter(lambda log: cls._is_bad_position(log, threshold), logs)
        flight_number = 1
        for period in periods:
            label = 'Flight {}'.format(flight_number)
            kml_flight = kml_folder.newfolder(name=label)
            flight_number += 1

            period_logs = filter(lambda x: cls._in_period(x, period), logs)
            if len(period_logs) < 2:
                continue

            coords = []
            angles = []
            when = []
            for entry in period_logs:
                pos = entry.uas_position.gps_position
                # Spatial Coordinates
                coord = (
                    pos.longitude,
                    pos.latitude,
                    entry.uas_position.altitude_msl,
                )
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

            for obstacle in MovingObstacle.objects.all():
                obstacle.kml(path=period_logs, kml=kml_flight, kml_doc=kml_doc)

    @classmethod
    def live_kml(cls, kml, timespan):
        users = User.objects.all()
        for user in users:
            all_logs = UasTelemetry.getAccessLogForUser(user)
            curr = timezone.now()
            period = (curr-timespan, curr)
            period_logs = filter(lambda x: cls._in_period(x, period), all_logs)

            if len(period_logs) < 1:
                continue

            linestring = kml.newlinestring(name=user.username)
            coords = []
            for entry in period_logs:
                pos = entry.uas_position.gps_position
                # Spatial Coordinates
                coord = (
                    pos.longitude,
                    pos.latitude,
                    entry.uas_position.altitude_msl,
                )
                coords.append(coord)
            linestring.coords = coords
            linestring.altitudemode = AltitudeMode.absolute
            linestring.extrude = 1
            linestring.style.linestyle.color = Color.blue
            linestring.style.polystyle.color = Color.changealphaint(100, Color.blue)

    @staticmethod
    def _in_period(log, period):
        """
        Determine if the log entry occurs during the given period.
        If time element is None, it is treated as unbound in that restriction

        Args:
            log: UasTelemetry element
            period: tuple( starting DateTime, ending DateTime)
        Returns:
            Boolean: True if in period, else False
        """
        if period[0] is None:
            return log.timestamp <= period[1]
        elif period[1] is None:
            return period[0] <= log.timestamp
        else:
            return period[0] <= log.timestamp <= period[1]

    @staticmethod
    def _is_bad_position(log, threshold):
        """
        Determine whether entry is not near latitude and longitude of 0,0.

        Args:
            x: UasTelemetry element
        Returns:
            Boolean: True if position is not near 0,0, else False
        """
        pos = log.uas_position.gps_position
        if max(abs(pos.latitude), abs(pos.longitude)) < threshold:
            return False
        return True
