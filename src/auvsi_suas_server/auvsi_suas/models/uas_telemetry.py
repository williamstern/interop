"""UAS Telemetry model."""

from access_log import AccessLog
from aerial_position import AerialPosition
from django.db import models
from math import pow
from math import sqrt
from simplekml import AltitudeMode
from simplekml import Color


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
    def kml(cls, user, logs, kml):
        """
        Appends kml nodes describing the given user's flight as described
        by the log array given.
        """
        pts = []
        threshold = 1  # Degrees
        kml_folder = kml.newfolder(name=user.username)

        for entry in logs:
            pos = entry.uas_position.gps_position
            mag = sqrt(pow(pos.latitude, 2)+pow(pos.longitude, 2))
            if mag < threshold:
                continue
            kml_entry = (
                pos.longitude,
                pos.latitude,
                entry.uas_position.altitude_msl,
            )
            pts.append(kml_entry)

        ls = kml_folder.newlinestring(
            name=user.username,
            coords=pts,
            altitudemode=AltitudeMode.absolute,
        )
        ls.extrude = 1
        ls.style.linestyle.width = 2
        ls.style.linestyle.color = Color.blue
