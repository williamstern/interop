"""Models for the AUVSI SUAS System."""

import datetime
from django.conf import settings
from django.db import models
from math import asin
from math import cos
from math import radians
from math import sin
from math import sqrt


def haversine(lon1, lat1, lon2, lat2):
      """
      Calculate the great circle distance between two points 
      on the earth (specified in decimal degrees).
      Reference:
      http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
      Args:
        lon1, lat1: The latitude and longitude of position 1
        lon2, lat2: The latitude and longitude of position 2
      Returns:
        The distance in kilometers
      """
      # convert decimal degrees to radians 
      lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

      # haversine formula 
      dlon = lon2 - lon1 
      dlat = lat2 - lat1 
      a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
      c = 2 * asin(sqrt(a)) 

      # 6367 km is the radius of the Earth
      km = 6367 * c
      return km


class GpsPosition(models.Model):
    """GPS position consisting of a latitude and longitude degree value."""
    # Latitude in degrees
    latitude = models.FloatField()
    # Longitude in degrees
    longitude = models.FloatField()

    def distanceTo(other):
        """Computes distance to another position.
        Args:
          other: The other position.
        Returns:
          Distance in feet.
        """
        km = haversine(longitude, latitude, other.longitude, other.latitude)
        # Convert km to feet
        ft = km * 3280.84
        return ft


class AerialPosition(models.Model):
    """Aerial position which consists of a GPS position and an altitude."""
    # GPS position
    gps_position = models.ForeignKey(GpsPosition)
    # MSL altitude in feet
    msl_altitude = models.FloatField()

    def distanceTo(other):
        """Computes distance to another position.
        Args:
          other: The other position.
        Returns:
          Distance in feet.
        """
        return math.hypot(math.abs(ms_altitude - other.msl_altitude),
                          gps_position.distanceTo(other.gps_position))


class Waypoint(models.Model):
    """A waypoint consists of an aerial position and a waypoint name."""
    # Aerial position
    position = models.ForeignKey(AerialPosition)
    # The name of the waypoint (optional)
    name = models.CharField(max_length=100)
    # Waypoint relative order number (optional)
    order = models.IntegerField()

    def distanceTo(other):
        """Computes distance to another waypoint.
        Args:
          other: The other waypoint.
        Returns:
          Distance in feet.
        """
        return position.distanceTo(other.position)


class ServerInfo(models.Model):
    """Static information stored on the server that teams must retrieve."""
    # Time information was stored
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    # Message for teams
    team_msg = models.CharField(max_length=100)


class ServerInfoAccessLog(models.Model):
    """Log of access to the ServoInfo objects used to evaluate teams."""
    # Timestamp of the access
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    # The user which accessed the data
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class Obstacle(models.Model):
    """An obstacle that teams must avoid."""
    # Obstacle name
    name = models.CharField(max_length=100)


class ObstacleAccessLog(models.Model):
    """Log of access ot the Obstacle objects used to evaulate teams."""
    # Timestamp of the access
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    # The user which accessed the data
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class StationaryObstacle(Obstacle):
    """A stationary obstacle that teams must avoid."""
    # The position of the obstacle center
    gps_position = models.ForeignKey(GpsPosition)
    # The radius of the cylinder in feet
    cylinder_radius = models.FloatField()
    # The height of the cylinder in feet
    cylinder_height = models.FloatField()


class MovingObstacle(Obstacle):
    """A moving obstacle that teams must avoid."""
    # The waypoints the obstacle attempts to follow
    waypoints = models.ManyToManyField(AerialPosition)
    # The max speed of the obstacle in knots
    speed_max = models.FloatField()
    # The radius of the sphere in feet
    sphere_radius = models.FloatField()


class UasTelemetry(models.Model):
    """UAS telemetry reported by teams."""
    # The user which generated the telemetry
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # The time at which the telemetry was received
    recv_timestamp = models.DateTimeField(default=datetime.datetime.now)
    # The position of the UAS
    uas_position = models.ForeignKey(AerialPosition)
    # The heading of the UAS in degrees (e.g. 0=north, 90=east)
    uas_heading = models.FloatField()
