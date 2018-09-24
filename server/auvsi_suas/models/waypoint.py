"""Waypoint model."""

from auvsi_suas.models.aerial_position import AerialPosition
from django.db import models


class Waypoint(models.Model):
    """A waypoint consists of an aerial position and its order in a set.

    Attributes:
        position: Aerial position.
        order: Waypoint relative order number. Should be unique per waypoint
            set.
    """
    position = models.ForeignKey(AerialPosition)
    order = models.IntegerField(db_index=True)

    def __str__(self):
        """Descriptive text for use in displays."""
        return "Waypoint (pk:%s, order:%s, pos:%s)" % (str(self.pk),
                                                       str(self.order),
                                                       str(self.position))

    def distance_to(self, other):
        """Computes distance to another waypoint.
        Args:
          other: The other waypoint.
        Returns:
          Distance in feet.
        """
        return self.position.distance_to(other.position)
