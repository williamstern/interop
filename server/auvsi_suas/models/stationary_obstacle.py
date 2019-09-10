"""Stationary obstacle model."""

import logging
from auvsi_suas.models.gps_position import GpsPositionMixin
from auvsi_suas.models.uas_telemetry import UasTelemetry
from django.contrib import admin
from django.core import validators
from django.db import models

logger = logging.getLogger(__name__)

STATIONARY_OBSTACLE_RADIUS_FT_MIN = 30
STATIONARY_OBSTACLE_RAIDUS_FT_MAX = 300


class StationaryObstacle(GpsPositionMixin):
    """A stationary obstacle that teams must avoid."""

    # The radius of the cylinder in feet.
    cylinder_radius = models.FloatField(validators=[
        validators.MinValueValidator(STATIONARY_OBSTACLE_RADIUS_FT_MIN),
        validators.MaxValueValidator(STATIONARY_OBSTACLE_RAIDUS_FT_MAX),
    ])
    # The height of the cylinder in feet.
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
        dist_to_center = self.distance_to(aerial_pos)
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
            if self.contains_pos(log):
                return True
        return False


@admin.register(StationaryObstacle)
class StationaryObstacleModelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'latitude', 'longitude', 'cylinder_radius',
                    'cylinder_height')
