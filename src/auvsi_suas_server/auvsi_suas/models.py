"""Models for the AUVSI SUAS System."""

import datetime
import numpy as np
import math
import time
from django.conf import settings
from django.core.cache import cache
from django.db import models
from scipy.interpolate import splrep, splev


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
    lon1 = math.radians(lon1)
    lat1 = math.radians(lat1)
    lon2 = math.radians(lon2)
    lat2 = math.radians(lat2)

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    hav_a = (math.sin(dlat/2)**2
             + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
    hav_c = 2 * math.asin(math.sqrt(hav_a))

    # 6367 km is the radius of the Earth
    dist_km = 6371 * hav_c
    return dist_km


def kilometersToFeet(kilometers):
    """Converts kilometers to feet.

    Args:
        kilometers: A distance in kilometers.
    Returns:
        A distance in feet.
    """
    return kilometers * 3280.8399


def knotsToFeetPerSecond(knots):
    """Converts knots to feet per second.

    Args:
        knots: A speed in knots.
    Returns:
        A speed in feet per second.
    """
    return knots * 1.6878098571011957


class GpsPosition(models.Model):
    """GPS position consisting of a latitude and longitude degree value."""
    # Latitude in degrees
    latitude = models.FloatField()
    # Longitude in degrees
    longitude = models.FloatField()

    def distanceTo(self, other):
        """Computes distance to another position.
        Args:
          other: The other position.
        Returns:
          Distance in feet.
        """
        dist = haversine(
                self.longitude, self.latitude, other.longitude, other.latitude)
        # Convert km to feet
        return kilometersToFeet(dist)


class AerialPosition(models.Model):
    """Aerial position which consists of a GPS position and an altitude."""
    # GPS position
    gps_position = models.ForeignKey(GpsPosition)
    # Above ground level (AGL) altitude in feet
    altitude_agl = models.FloatField()

    def distanceTo(self, other):
        """Computes distance to another position.
        Args:
          other: The other position.
        Returns:
          Distance in feet.
        """
        return math.hypot(abs(self.altitude_agl - other.altitude_agl),
                          self.gps_position.distanceTo(other.gps_position))


class Waypoint(models.Model):
    """A waypoint consists of an aerial position and its order in a set."""
    # Aerial position
    position = models.ForeignKey(AerialPosition)
    # Waypoint relative order number. Should be unique per waypoint set.
    order = models.IntegerField()

    def distanceTo(self, other):
        """Computes distance to another waypoint.
        Args:
          other: The other waypoint.
        Returns:
          Distance in feet.
        """
        return self.position.distanceTo(other.position)


class ServerInfo(models.Model):
    """Static information stored on the server that teams must retrieve."""
    # Time information was stored
    timestamp = models.DateTimeField(auto_now=True)
    # Message for teams
    team_msg = models.CharField(max_length=100)

    def toJSON(self):
        """Obtain a JSON style representation of object."""
        data = {
            'message': self.team_msg,
            'message_timestamp': str(self.timestamp)
        }
        return data


class ServerInfoAccessLog(models.Model):
    """Log of access to the ServerInfo objects used to evaluate teams."""
    # Timestamp of the access
    timestamp = models.DateTimeField(auto_now=True)
    # The user which accessed the data
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class ObstacleAccessLog(models.Model):
    """Log of access ot the Obstacle objects used to evaulate teams."""
    # Timestamp of the access
    timestamp = models.DateTimeField(auto_now=True)
    # The user which accessed the data
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class StationaryObstacle(models.Model):
    """A stationary obstacle that teams must avoid."""
    # The position of the obstacle center
    gps_position = models.ForeignKey(GpsPosition)
    # The radius of the cylinder in feet
    cylinder_radius = models.FloatField()
    # The height of the cylinder in feet
    cylinder_height = models.FloatField()

    def containsPos(self, aerial_pos):
        """Whether the pos is contained within the obstacle."""
        # Check altitude of position
        aerial_alt = aerial_pos.altitude_agl
        if aerial_alt < 0 or aerial_alt > self.cylinder_height:
            return False
        # Check lat/lon of position
        dist_to_center = self.gps_position.distanceTo(aerial_pos.gps_position)
        if dist_to_center > self.cylinder_radius:
            return False
        # Both within altitude and radius bounds, inside cylinder
        return True

    def toJSON(self):
        """Obtain a JSON style representation of object."""
        if self.gps_position is None:
            latitude = 0
            longitude = 0
        else:
            latitude = self.gps_position.latitude
            longitude = self.gps_position.longitude
        data = {
            'latitude':  latitude,
            'longitude': longitude,
            'cylinder_radius': self.cylinder_radius,
            'cylinder_height': self.cylinder_height
        }
        return data


class MovingObstacle(models.Model):
    """A moving obstacle that teams must avoid."""
    # The waypoints the obstacle attempts to follow
    waypoints = models.ManyToManyField(Waypoint)
    # The average speed of the obstacle in knots
    speed_avg = models.FloatField()
    # The radius of the sphere in feet
    sphere_radius = models.FloatField()

    def containsPos(self, obst_pos, aerial_pos):
        """Whether the pos is contained within the obstacle's pos."""
        dist_to_center = obst_pos.distanceTo(aerial_pos)
        return dist_to_center <= self.sphere_radius

    def getWaypointTravelTime(self, waypoints, id_tm1, id_t):
        """Gets the travel time to the current waypoint from a previous.

        Args:
          waypoints: A set of sorted waypoints which define a path.
          id_tm1: The ID of the starting waypoint.
          id_t: The ID of the ending waypoint.
        Returns:
          Time to travel between the two waypoints in seconds. Returns None on
          error.
        """
        # Validate inputs
        if (not waypoints
            or len(waypoints) < 2
            or id_tm1 is None
            or id_t is None
            or id_tm1 < 0 or id_tm1 >= len(waypoints)
            or id_t < 0 or id_t >= len(waypoints)
            or self.speed_avg <= 0):
            # Invalid inputs
            return None

        waypoint_t = waypoints[id_t]
        waypoint_tm1 = waypoints[id_tm1]
        waypoint_dist = waypoint_tm1.distanceTo(waypoint_t)
        speed_avg_fps = knotsToFeetPerSecond(self.speed_avg)
        waypoint_travel_time = waypoint_dist / speed_avg_fps

        return waypoint_travel_time

    def getInterWaypointTravelTimes(self, waypoints):
        """Computes the travel times for the waypoints.

        Args:
            waypoints: A list of waypoints defining a circular path.
        Returns:
            A numpy array of travel times between waypoints. The first value is
            between waypoint 0 and 1, the last between N and 0.
        """
        num_waypoints = len(waypoints)
        travel_times = np.zeros(num_waypoints + 1)
        for waypoint_id in range(1, num_waypoints+1):
            # Current intra waypoint travel time
            id_tm1 = (waypoint_id - 1) % num_waypoints
            id_t = waypoint_id % num_waypoints
            cur_travel_time = self.getWaypointTravelTime(
                waypoints, id_tm1, id_t)
            travel_times[waypoint_id] = cur_travel_time

        return travel_times


    def getWaypointTimes(self, waypoint_travel_times):
        """Computes the time at which the obstacle will be at each waypoint.

        Args:
            waypoint_travel_time: The inter-waypoint travel times generated by
                getInterWaypiontTravelTimes() or equivalent.
        Returns:
            A numpy array of waypoint times.
        """
        total_time = 0
        num_paths = len(waypoint_travel_times)
        pos_times = np.zeros(num_paths)
        for path_id in range(num_paths):
            total_time += waypoint_travel_times[path_id]
            pos_times[path_id] = total_time

        return pos_times

    def getSplineCurve(self, waypoints):
        """Computes spline curve representation to match waypoints.

        Args:
            waypoints: The waypoints to calculate a spline curve from.
        Returns:
            A tuple (total_travel_time, spline_reps) where total_travel_time is
            the total time to complete a circuit, and spline_reps is a list of
            tck values generated from spline creation. The list is ordered
            latitude, longitude, altitude.
        """
        num_waypoints = len(waypoints)

        # Store waypoint data for interpolation
        positions = np.zeros((num_waypoints + 1, 3))
        for waypoint_id in range(num_waypoints):
            cur_waypoint = waypoints[waypoint_id]
            cur_position = cur_waypoint.position
            cur_gps_pos = cur_position.gps_position
            positions[waypoint_id, 0] = cur_gps_pos.latitude
            positions[waypoint_id, 1] = cur_gps_pos.longitude
            positions[waypoint_id, 2] = cur_position.altitude_agl

        # Get the intra waypoint travel times
        waypoint_travel_times = self.getInterWaypointTravelTimes(waypoints)
        # Get the waypoint times
        pos_times = self.getWaypointTimes(waypoint_travel_times)
        total_travel_time = pos_times[len(pos_times)-1]

        # Create spline representation
        spline_k = 3 if num_waypoints >= 3 else 2  # Cubic if enough points
        spline_reps = list()
        for iter_dim in range(3):
            tck = splrep(pos_times, positions[:,iter_dim], k=spline_k, per=1)
            spline_reps.append(tck)

        return (total_travel_time, spline_reps)

    def getWaypointsCacheKey(self):
        """Gets the cache key for this objects deduped waypoints."""
        return '/MovingObstacle/%d/waypoints' % self.id

    def getSplineCurveCacheKey(self):
        """Gets the cache key for this objects spline curve rep."""
        return '/MovingObstacle/%d/spline_curve' % self.id

    def getPosition(self, cur_time=datetime.datetime.now()):
        """Gets the current position for the obstacle.

        Args:
          cur_time: The current time as datetime.
        Returns:
          Returns a tuple (latitude, longitude, altitude_agl) for the obstacle
          at the given time.
        """
        # Get waypoints
        waypoints_key = self.getWaypointsCacheKey()
        waypoints = cache.get(waypoints_key)
        if waypoints is None:
            # Load waypoints for obstacle, filter for consecutive duplicates
            all_wpts = self.waypoints.order_by('order')
            waypoints = [
                    all_wpts[i]
                    for i in range(len(all_wpts))
                    if i == 0 or all_wpts[i].distanceTo(all_wpts[i-1]) != 0]
            cache.set(waypoints_key, waypoints)

        # Waypoint counts of 0 or 1 can skip calc, so can no speed
        num_waypoints = len(waypoints)
        if num_waypoints == 0:
            return (0, 0, 0)  # Undefined position
        elif num_waypoints == 1 or self.speed_avg <= 0:
            wpt = waypoints[0]
            return (wpt.position.gps_position.latitude,
                    wpt.position.gps_position.longitude,
                    wpt.position.altitude_agl)

        # Get spline representation
        spline_curve_key = self.getSplineCurveCacheKey()
        spline_curve = cache.get(spline_curve_key)
        if spline_curve is None:
            spline_curve = self.getSplineCurve(waypoints)
            cache.set(spline_curve_key, spline_curve)
        (total_travel_time, spline_reps) = spline_curve

        # Sample spline at current time
        cur_time_sec = (cur_time -
                datetime.datetime.utcfromtimestamp(0)).total_seconds()
        cur_path_time = np.mod(cur_time_sec, total_travel_time)
        latitude = float(splev(cur_path_time, spline_reps[0]))
        longitude = float(splev(cur_path_time, spline_reps[1]))
        altitude_agl = float(splev(cur_path_time, spline_reps[2]))

        return (latitude, longitude, altitude_agl)

    def toJSON(self):
        """Obtain a JSON style representation of object."""
        (latitude, longitude, altitude_agl) = self.getPosition()
        data = {
            'latitude': latitude,
            'longitude': longitude,
            'altitude_agl': altitude_agl,
            'sphere_radius': self.sphere_radius
        }
        return data


class UasTelemetry(models.Model):
    """UAS telemetry reported by teams."""
    # The user which generated the telemetry
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # The time at which the telemetry was received
    recv_timestamp = models.DateTimeField(auto_now=True)
    # The position of the UAS
    uas_position = models.ForeignKey(AerialPosition)
    # The heading of the UAS in degrees (e.g. 0=north, 90=east)
    uas_heading = models.FloatField()


class FlyZone(models.Model):
    """An approved area for UAS flight. UAS shall be in at least one zone."""
    # The polygon defining the boundary of the zone.
    boundary_pts = models.ManyToManyField(Waypoint)
    # The minimum altitude of the zone (AGL) in feet
    altitude_agl_min = models.FloatField()
    # The maximum altitude of the zone (AGL) in feet
    altitude_agl_max = models.FloatField()


class TakeoffOrLandingEvent(models.Model):
    """Marker for a UAS takeoff/landing. UAS must interop during that time."""
    # The user for which the event applies
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # Whether the UAS is now in the air
    uas_in_air = models.BooleanField()


class MissionConfig(models.Model):
    """The details for the active mission. There should only be one."""
    # The home position for use as a reference point. Should be the tents.
    home_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_home_pos")
    # The waypoints that define the mission waypoint path
    mission_waypoints = models.ManyToManyField(
            Waypoint, related_name="missionconfig_mission_waypoints")
    # The polygon that defines the search grid
    search_grid_points = models.ManyToManyField(
            Waypoint, related_name="missionconfig_search_grid_points")
    # The polygon that defines the emergent target search grid
    emergent_grid_points = models.ManyToManyField(
            Waypoint, related_name="missionconfig_emergent_grid_points")
    # The last known position of the emergent target
    emergent_last_known_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_emergent_last_known_pos")
    # Off-axis target position
    off_axis_target_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_off_axis_target_pos")
    # The SRIC position
    sric_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_sric_pos")
    # The IR target position
    ir_target_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_ir_target_pos")
    # The air drop position
    air_drop_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_air_drop_pos")
