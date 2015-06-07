"""UAS Telemetry model."""

from access_log import AccessLog
from aerial_position import AerialPosition
from auvsi_suas.models.moving_obstacle import MovingObstacle
from django.db import models
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

        coords = []
        angles = []
        when = []
        kml_folder = kml.newfolder(name=user.username)

        def is_not_zero(x):
            """
            Determine whether entry is not near latitude and longitude of 0,0.

            Args:
                x: UasTelemetry element
            Returns:
                Boolean: True if position is not near 0,0, else False
            """
            pos = x.uas_position.gps_position
            if max(abs(pos.latitude), abs(pos.longitude)) < threshold:
                return False
            return True
        logs = filter(is_not_zero, logs)

        for entry in logs:
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
        trk = kml_folder.newgxtrack(name='Flight Path')
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
            obstacle.kml(path=logs, kml=kml_folder, kml_doc=kml_doc)
