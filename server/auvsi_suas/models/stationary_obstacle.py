"""Stationary obstacle model."""

import logging
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.uas_telemetry import UasTelemetry
from django.contrib import admin
from django.db import models

logger = logging.getLogger(__name__)


class StationaryObstacle(models.Model):
    """A stationary obstacle that teams must avoid.

    Attributes:
        gps_position: The position of the obstacle center.
        cylinder_radius: The radius of the cylinder in feet.
        cylinder_height: The height of the cylinder in feet.
    """
    gps_position = models.ForeignKey(GpsPosition, on_delete=models.CASCADE)
    cylinder_radius = models.FloatField()
    cylinder_height = models.FloatField()

    def contains_pos(self, aerial_pos):
        """Whether the pos is contained within the obstacle.

        Args:
            aerial_pos: The AerialPosition to test.
        Returns:
            Whether the given position is inside the obstacle.
        """
        # Check altitude of position
        aerial_alt = aerial_pos.altitude_msl
        if aerial_alt > self.cylinder_height:
            return False
        # Check lat/lon of position
        dist_to_center = self.gps_position.distance_to(aerial_pos.gps_position)
        return dist_to_center <= self.cylinder_radius

    def evaluate_collision_with_uas(self, uas_telemetry_logs):
        """Evaluates whether the Uas logs indicate a collision.

        Args:
            uas_telemetry_logs: A list of UasTelemetry logs sorted by timestamp
                for which to evaluate.
        Returns:
            Whether a UAS telemetry log reported indicates a collision with the
            obstacle.
        """
        for log in UasTelemetry.interpolate(uas_telemetry_logs):
            if self.contains_pos(log.uas_position):
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


@admin.register(StationaryObstacle)
class StationaryObstacleModelAdmin(admin.ModelAdmin):
    raw_id_fields = ("gps_position", )
    list_display = ('gps_position', 'cylinder_radius', 'cylinder_height')
