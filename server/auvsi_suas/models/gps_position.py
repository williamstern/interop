"""GPS position model."""

from auvsi_suas.models import distance
from django.db import models


class GpsPosition(models.Model):
    """GPS position consisting of a latitude and longitude degree value."""
    # Latitude in degrees
    latitude = models.FloatField()
    # Longitude in degrees
    longitude = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("GpsPosition (pk:%s, lat:%s, lon:%s)" %
                       (str(self.pk), str(self.latitude), str(self.longitude)))

    def distanceTo(self, other):
        """Computes distance to another position.

        Args:
          other: The other position.
        Returns:
          Distance in feet.
        """
        return distance.distanceTo(
                self.latitude, self.longitude, 0,
                other.latitude, other.longitude, 0)

