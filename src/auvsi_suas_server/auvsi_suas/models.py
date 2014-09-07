from django.conf import settings
from django.db import models


class GpsPosition(models.Model):
    """GPS position consisting of a latitude and longitude degree value."""
    # The name of the position. Used to uniquely identify it.
    position_name = models.CharField(max_length=100)
    # Latitude in degrees
    latitude = models.FloatField()
    # Longitude in degrees
    longitude = models.FloatField()


class AerialPosition(models.Model):
    """Aerial position which consists of a GPS position and an altitude."""
    # GPS position
    gps_position = models.ForeignKey(GpsPosition)
    # MSL altitude in feet
    msl_altitude = models.FloatField()


class Waypoint(models.Model):
    """A waypoint consists of an aerial position and a waypoint name."""
    # The name of the waypoint
    name = models.CharField(max_length=100)
    # Aerial position
    position = models.ForeignKey(AerialPosition)


class ServerInfo(models.Model):
    """Static information stored on the server that teams must retrieve."""
    # Time information was stored
    timestamp = models.DateTimeField(auto_now_add=True)
    # Message for teams
    team_msg = models.CharField(max_length=100)


class ServerInfoAccessLog(models.Model):
    """Log of access to the ServoInfo objects used to evaluate teams."""
    # Timestamp of the access
    timestamp = models.DateTimeField(auto_now_add=True)
    # The user which accessed the data
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class Obstacle(models.Model):
    """An obstacle that teams must avoid."""
    # Obstacle name
    name = models.CharField(max_length=100)


class ObstacleAccessLog(models.Model):
    """Log of access ot the Obstacle objects used to evaulate teams."""
    # Timestamp of the access
    timestamp = models.DateTimeField(auto_now_add=True)
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
    # The max speed of the obstacle
    speed_max = models.FloatField()
    # The radius of the sphere in feet
    sphere_radius = models.FloatField()


class UasTelemetry(models.Model):
    """UAS telemetry reported by teams."""
    # The user which generated the telemetry
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # The time at which the telemetry was received
    recv_timestamp = models.DateTimeField(auto_now_add=True)
    # The position of the UAS
    uas_position = models.ForeignKey(AerialPosition)
    # The heading of the UAS in degrees (e.g. 0=north, 90=east)
    uas_heading = models.FloatField()
