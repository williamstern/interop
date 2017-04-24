"""Stationary obstacle model."""

import numpy as np

from auvsi_suas.models import distance
from gps_position import GpsPosition
from django.conf import settings
from django.db import models


class StationaryObstacle(models.Model):
    """A stationary obstacle that teams must avoid.

    Attributes:
        gps_position: The position of the obstacle center.
        cylinder_radius: The radius of the cylinder in feet.
        cylinder_height: The height of the cylinder in feet.
    """
    gps_position = models.ForeignKey(GpsPosition)
    cylinder_radius = models.FloatField()
    cylinder_height = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("StationaryObstacle (pk:%s, radius:%s, height:%s, "
                       "gps:%s)" % (str(self.pk), str(self.cylinder_radius),
                                    str(self.cylinder_height),
                                    self.gps_position.__unicode__()))

    def cylinder_collision(self, start_log, end_log, utm):
        # Verify that aircraft velocity is within bounds. Don't interpolate if
        # it isn't because the data is probably erroneous.
        d = start_log.uas_position.distance_to(end_log.uas_position)
        t = (end_log.timestamp - start_log.timestamp).total_seconds()
        if (t > settings.MAX_TELMETRY_INTERPOLATE_INTERVAL_SEC or
            (d / t) > settings.MAX_AIRSPEED_FT_PER_SEC):
            return self.contains_pos(end_log.uas_position)

        def get_projected(aerial_pos):
            lat = aerial_pos.gps_position.latitude
            lon = aerial_pos.gps_position.longitude
            return pyproj.transform(wgs84, utm, lon, lat)

        x1, y1 = get_projected(start_log.uas_position.gps_position)
        z1 = units.feet_to_meters(start_log.uas_position.altitude_msl)
        x2, y2 = get_projected(end_log.uas_position.gps_position)
        z2 = units.feet_to_meters(end_log.uas_position.altitude_msl)

        cx, cy = get_projected(self.gps_position)

        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        # x^2 + (mx + b)^2 = r^2
        # x^2 + m^2x^2 + 2mxb + b^2 = r^2
        # (m^2 + 1)x^2 + (2mb) x + (b^2 - r^2)
        p = [m*m + 1, 2*m*b, b*b - self.cylinder_radius * self.cylinder_radius]
        roots = np.roots(p)

        for root in roots:
            zcalc = ((root - x1) * (z2 - z1) / (x2 - x1)) + z1
            if (zcalc > 0 and zcalc < self.cylinder_height):
                return True


    def contains_pos(self, aerial_pos):
        """Whether the pos is contained within the obstacle.

        Args:
            aerial_pos: The AerialPosition to test.
        Returns:
            Whether the given position is inside the obstacle.
        """
        # Check altitude of position
        aerial_alt = aerial_pos.altitude_msl
        if (aerial_alt < 0 or aerial_alt > self.cylinder_height):
            return False
        # Check lat/lon of position
        dist_to_center = self.gps_position.distance_to(aerial_pos.gps_position)
        if dist_to_center > self.cylinder_radius:
            return False
        # Both within altitude and radius bounds, inside cylinder
        return True

    def evaluate_collision_with_uas(self, uas_telemetry_logs):
        """Evaluates whether the Uas logs indicate a collision.

        Args:
            uas_telemetry_logs: A list of UasTelemetry logs sorted by timestamp
                for which to evaluate.
        Returns:
            Whether a UAS telemetry log reported indicates a collision with the
            obstacle.
        """
        zone, north = distance.utm_zone(self.gps_position.latitude,
                                        self.gps_position.longitude)
        utm = distance.proj_utm(zone, north)
        for i in range(0, len(uas_telemetry_logs)):
            cur_log = uas_telemetry_logs[i]
            if i > 0:
                cur_log = uas_telemetry_logs[i]
                prev_log = uas_telemetry_logs[i - 1]
                if self.cylinder_collision(uas_telemetry_logs[i-1],
                                           uas_telemetry_logs[i], utm):
                    return True
            else:
                if self.contains_pos(cur_log.uas_position):
                    return True
        return False

    def json(self):
        """Obtain a JSON style representation of object."""
        if self.gps_position is None:
            latitude = 0
            longitude = 0
        else:
            latitude = self.gps_position.latitude
            longitude = self.gps_position.longitude

        data = {
            'latitude': latitude,
            'longitude': longitude,
            'cylinder_radius': self.cylinder_radius,
            'cylinder_height': self.cylinder_height
        }
        return data
