from django.db import models

class GpsPosition(models.Model):
    """GPS position consisting of a latitude and longitude degree value."""
    # Latitude in degrees
    latitude = models.FloatField()
    # Longitude in degrees
    longitude = models.FloatField()


class Waypoint(models.Model):
    """Waypoint position which consists of a GPS position and an altitude."""
    # GPS position
    gps_position = models.ForeignKey(GpsPosition)
    # MSL altitude in feet
    msl_altitude = models.FloatField()


class ServerInfo(models.Model):
    """Static information stored on the server that teams must retrieve."""
    # Time information was stored
    timestamp = models.DateTimeField(auto_now_add=True)
    # Message for users
    user_msg = models.CharField(max_length=100)


class Obstacle(models.Model):
    """An obstacle that teams must avoid."""
    # Obstacle name
    name = models.CharField(max_length=100)


class StationaryObstacle(Obstacle):
    """A stationary obstacle that teams must avoid."""
    # The position of the obstacle center
    gps_position = models.ForeignKey(GpsPosition)
    # The radius of the cylinder in feet
    radius = models.FloatField()
    # The height of the cylinder in feet
    height = models.FloatField()


class MovingObstacle(Obstacle):
    """A moving obstacle that teams must avoid."""
    # The position of the obstacle center
    position = models.ForeignKey(Waypoint) 
    # The radius of the sphere in feet
    radius = models.FloatField()


class Team(models.Model):
    """A team at the AUVSI SUAS competition."""
    # Human readable team name
    team_name = models.CharField(max_length=100)


class AircraftTelemetry(models.Model):
    """Aircraft telemetry reported by teams."""
    # The team which generated the telemetry
    team = models.ForeignKey(Team)
    # The time at which the telemetry was received
    recv_timestamp = models.DateTimeField(auto_now_add=True)
    # The position of the aircraft
    position = models.ForeignKey(Waypoint)
    # The heading of the aircraft in degrees (e.g. 0=north, 90=east)
    heading = models.FloatField()
