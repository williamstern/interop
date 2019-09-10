"""Waypoint model."""

import logging
from auvsi_suas.models.aerial_position import AerialPositionMixin
from django.contrib import admin
from django.db import models

logger = logging.getLogger(__name__)


class Waypoint(AerialPositionMixin):
    """A waypoint consists of an aerial position and its order in a set."""

    # Waypoint relative order number. Should be unique per waypoint set.
    order = models.IntegerField(db_index=True)

    def distance_to(self, other):
        """Computes distance to another waypoint.
        Args:
          other: The other waypoint.
        Returns:
          Distance in feet.
        """
        return super(Waypoint, self).distance_to(other)


@admin.register(Waypoint)
class WaypointModelAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('pk', 'order', 'latitude', 'longitude', 'altitude_msl')
