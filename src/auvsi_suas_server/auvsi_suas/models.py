"""Models for the AUVSI SUAS System."""

import datetime
import logging
import numpy as np
import math
import time
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from matplotlib import path as mplpath
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

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("GpsPosition (pk:%d, lat:%f, lon:%f)" %
                       (self.pk, self.latitude, self.longitude))

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
    altitude_msl = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("AerialPosition (pk:%d, alt:%f, gps:%s)" %
                       (self.pk, self.altitude_msl,
                        self.gps_position.__unicode__()))

    def distanceTo(self, other):
        """Computes distance to another position.
        Args:
          other: The other position.
        Returns:
          Distance in feet.
        """
        return math.hypot(abs(self.altitude_msl - other.altitude_msl),
                          self.gps_position.distanceTo(other.gps_position))


class Waypoint(models.Model):
    """A waypoint consists of an aerial position and its order in a set."""
    # Aerial position
    position = models.ForeignKey(AerialPosition)
    # Waypoint relative order number. Should be unique per waypoint set.
    order = models.IntegerField(db_index=True)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("Waypoint (pk:%d, order:%d, pos:%s)" %
                       (self.pk, self.order, self.position.__unicode__()))

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
    timestamp = models.DateTimeField(auto_now_add=True)
    # Message for teams
    team_msg = models.CharField(max_length=100)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("ServerInfo (pk:%d, msg:%s, timestamp:%s)" %
                       (self.pk, self.team_msg, str(self.timestamp)))

    def toJSON(self):
        """Obtain a JSON style representation of object."""
        data = {
            'message': self.team_msg,
            'message_timestamp': str(self.timestamp)
        }
        return data


class AccessLog(models.Model):
    """Base class which logs access of information."""
    # Timestamp of the access
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    # The user which accessed the data
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("%s (pk:%d, user:%s, timestamp:%s)" %
                       (self.__class__.__name__, self.pk,
                        self.user.__unicode__(), str(self.timestamp)))


    @classmethod
    def getAccessLogForUser(cls, user):
        """Gets the time-sorted list of access log for the given user.

        Args:
            user: The user to get the access log for.
        Returns:
            A list of access log objects for the given user sorted by timestamp.
        """
        return cls.objects.filter(user_id=user.pk).order_by('timestamp')

    @classmethod
    def getAccessLogForUserByTimePeriod(cls, access_logs, time_periods):
        """Gets a list of time-sorted lists of access logs for each time period.

        Args:
            access_logs: A list of access logs for a given user sorted by
                timestamp.
            time_periods: A sorted list of (time_start, time_end) tuples which
                indicate the start and end time of a time period. A value of
                None indicates infinity. The list must be sorted by time_start
                and be non-intersecting.
        Returns:
            A list where each entry is a list of access logs sorted by timestamp
            such that each log is for the given user and in the time period
            given in the time_periods list.
        """
        cur_access_id = 0
        cur_time_id = 0
        time_period_access_logs = list()
        while (cur_access_id < len(access_logs) and
               cur_time_id < len(time_periods)):
            # Add new period access list if not yet added for current period
            if cur_time_id == len(time_period_access_logs):
                time_period_access_logs.append(list())
            # Get the current time period and access log
            cur_time = time_periods[cur_time_id]
            (time_start, time_end) = cur_time
            cur_access = access_logs[cur_access_id]
            # Check if access log before the period, indicates not in a period
            if time_start is not None and cur_access.timestamp < time_start:
                cur_access_id += 1
                continue
            # Check if access log after the period
            if time_end is not None and cur_access.timestamp > time_end:
                cur_time_id += 1
                continue
            # Access log not before and not after, so its during. Add the log
            time_period_access_logs[cur_time_id].append(cur_access)
            cur_access_id += 1

        # Add empty lists for all remaining time periods
        while len(time_period_access_logs) < len(time_periods):
            time_period_access_logs.append(list())

        return time_period_access_logs

    @classmethod
    def getAccessLogRates(
            cls, time_periods, time_period_access_logs):
        """Gets the access log rates.

        Args:
            time_periods: A list of (time_start, time_end) tuples sorted by
                time_start indicating time periods of interest where None
                indicates infinity.
            time_period_access_logs: A list of access log lists for each time
                period.
        Returns:
            A (min, max, avg) tuple. The min is the min time between logs, max
            is the max time between logs, and avg is the avg time between logs.
            """
        times_between_logs = list()
        for time_period_id in range(len(time_periods)):
            # Get the times and logs for this period
            (time_start, time_end) = time_periods[time_period_id]
            cur_access_logs = time_period_access_logs[time_period_id]

            # Account for a time period with no logs
            if len(cur_access_logs) == 0:
                if time_start is not None and time_end is not None:
                    time_diff = (time_end - time_start).total_seconds()
                    times_between_logs.append(time_diff)
                continue

            # Account for time between takeoff and first log
            if time_start is not None:
                first_log = cur_access_logs[0]
                time_diff = (first_log.timestamp - time_start).total_seconds()
                times_between_logs.append(time_diff)
            # Account for time between logs
            for access_log_id in range(len(cur_access_logs)-1):
                log_t = cur_access_logs[access_log_id]
                log_tp1 = cur_access_logs[access_log_id+1]
                time_diff = (log_tp1.timestamp -
                        log_t.timestamp).total_seconds()
                times_between_logs.append(time_diff)
            # Account for time between last log and landing
            if time_end is not None:
                last_log = cur_access_logs[len(cur_access_logs)-1]
                time_diff = (time_end - last_log.timestamp).total_seconds()
                times_between_logs.append(time_diff)

        # Compute log rates
        if times_between_logs:
            times_between_logs = np.array(times_between_logs)
            times_between_min = np.min(times_between_logs)
            times_between_max = np.max(times_between_logs)
            times_between_avg = np.mean(times_between_logs)
            return (times_between_min,
                    times_between_max,
                    times_between_avg)
        else:
            return (None, None, None)


class ServerInfoAccessLog(AccessLog):
    """Log of access to the ServerInfo objects used to evaluate teams."""


class ObstacleAccessLog(AccessLog):
    """Log of access to the Obstacle objects used to evaulate teams."""


class UasTelemetry(AccessLog):
    """UAS telemetry reported by teams."""
    # The position of the UAS
    uas_position = models.ForeignKey(AerialPosition)
    # The heading of the UAS in degrees (e.g. 0=north, 90=east)
    uas_heading = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("UasTelemetry (pk:%d, user:%s, timestamp:%s, "
                       "heading:%f, pos:%s)" %
                       (self.pk, self.user.__unicode__(),
                        str(self.timestamp), self.uas_heading,
                        self.uas_position.__unicode__()))


class TakeoffOrLandingEvent(AccessLog):
    """Marker for a UAS takeoff/landing. UAS must interop during that time."""
    # Whether the UAS is now in the air
    uas_in_air = models.BooleanField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode('TakeoffOrLandingEvent (pk%d, user:%s, timestamp:%s, '
                       'uas_in_air:%s)' %
                       (self.pk, self.user.__unicode__(), self.timestamp,
                        str(self.uas_in_air)))

    @classmethod
    def getFlightPeriodsForUser(cls, user):
        """Gets the time period for which the given user was in flight.

        Args:
            user: The user for which to get flight periods for.
        Returns:
            A list of (flight_start, flight_end) tuples where flight_start is
            the time the flight started and flight_end is the time the flight
            ended.  This is based off the takeoff and landing events stored. A
            flight_X of None indicates since the beginning or until the end of
            time. The list will be sorted by flight_start and the periods will
            be non-intersecting.
        """
        time_periods = list()
        # Get the access logs for the user
        access_logs = TakeoffOrLandingEvent.getAccessLogForUser(user)

        # If UAS in air at start, assume forgot to log takeoff, assign infinity
        if len(access_logs) > 0 and not access_logs[0].uas_in_air:
            time_periods.append((None, access_logs[0].timestamp))

        # Use transition from ground to air and air to ground for flight periods
        takeoff_time = None
        landing_time = None
        uas_in_air = False
        for cur_log in access_logs:
            # Check for transition from ground to air
            if not uas_in_air and cur_log.uas_in_air:
                takeoff_time = cur_log.timestamp
                uas_in_air = cur_log.uas_in_air
            # Check for transition from air to ground
            if uas_in_air and not cur_log.uas_in_air:
                landing_time = cur_log.timestamp
                uas_in_air = cur_log.uas_in_air
                time_periods.append((takeoff_time, landing_time))

        # If UAS in air at end, assume forgot to log landing, assign infinity
        if uas_in_air:
            time_periods.append((access_logs[len(access_logs)-1].timestamp,
                                 None))

        return time_periods


class StationaryObstacle(models.Model):
    """A stationary obstacle that teams must avoid."""
    # The position of the obstacle center
    gps_position = models.ForeignKey(GpsPosition)
    # The radius of the cylinder in feet
    cylinder_radius = models.FloatField()
    # The height of the cylinder in feet
    cylinder_height = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("StationaryObstacle (pk:%d, radius:%f, height:%f, "
                       "gps:%s)" %
                       (self.pk, self.cylinder_radius, self.cylinder_height,
                        self.gps_position.__unicode__()))


    def containsPos(self, aerial_pos):
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
        dist_to_center = self.gps_position.distanceTo(aerial_pos.gps_position)
        if dist_to_center > self.cylinder_radius:
            return False
        # Both within altitude and radius bounds, inside cylinder
        return True

    def evaluateCollisionWithUas(self, uas_telemetry_logs):
        """Evaluates whether the Uas logs indicate a collision.

        Args:
            uas_telemetry_logs: A list of UasTelemetry logs sorted by timestamp
                for which to evaluate.
        Returns:
            Whether a UAS telemetry log reported indicates a collision with the
            obstacle.
        """
        for cur_log in uas_telemetry_logs:
            if self.containsPos(cur_log.uas_position):
                return True
        return False

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

    def __unicode__(self):
        """Descriptive text for use in displays."""
        waypoints_strs = ["%s" % wpt.__unicode__()
                          for wpt in self.waypoints.all()]
        waypoints_str = ", ".join(waypoints_strs)
        return unicode("MovingObstacle (pk:%d, speed:%f, radius:%f, "
                       "waypoints:[%s])" %
                       (self.pk, self.speed_avg, self.sphere_radius,
                        waypoints_str))

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
            positions[waypoint_id, 2] = cur_position.altitude_msl

        # Get the intra waypoint travel times
        waypoint_travel_times = self.getInterWaypointTravelTimes(waypoints)
        # Get the waypoint times
        pos_times = self.getWaypointTimes(waypoint_travel_times)
        total_travel_time = pos_times[len(pos_times)-1]

        # Create spline representation
        spline_k = 3 if num_waypoints >= 3 else 2  # Cubic if enough points
        spline_reps = list()
        for iter_dim in range(3):
            tck = splrep(pos_times, positions[:, iter_dim], k=spline_k, per=1)
            spline_reps.append(tck)

        return (total_travel_time, spline_reps)

    def getPosition(self, cur_time=timezone.now()):
        """Gets the current position for the obstacle.

        Args:
          cur_time: The current time as datetime with time zone.
        Returns:
          Returns a tuple (latitude, longitude, altitude_msl) for the obstacle
          at the given time.
        """
        # Get waypoints
        if hasattr(self, 'preprocessed_waypoints'):
            waypoints = self.preprocessed_waypoints
        else:
            # Load waypoints for obstacle, filter for consecutive duplicates
            all_wpts = self.waypoints.order_by('order')
            waypoints = [
                    all_wpts[i]
                    for i in range(len(all_wpts))
                    if i == 0 or all_wpts[i].distanceTo(all_wpts[i-1]) != 0]
            self.preprocessed_waypoints = waypoints

        # Waypoint counts of 0 or 1 can skip calc, so can no speed
        num_waypoints = len(waypoints)
        if num_waypoints == 0:
            return (0, 0, 0)  # Undefined position
        elif num_waypoints == 1 or self.speed_avg <= 0:
            wpt = waypoints[0]
            return (wpt.position.gps_position.latitude,
                    wpt.position.gps_position.longitude,
                    wpt.position.altitude_msl)

        # Get spline representation
        if hasattr(self, 'preprocessed_spline_curve'):
            spline_curve = self.preprocessed_spline_curve
        else:
            spline_curve = self.getSplineCurve(waypoints)
            self.preprocessed_spline_curve = spline_curve
        (total_travel_time, spline_reps) = spline_curve

        # Sample spline at current time
        epoch_time = timezone.now().replace(
                year=1970, month=1, day=1, hour=0, minute=0, second=0,
                microsecond=0)
        cur_time_sec = (cur_time - epoch_time).total_seconds()
        cur_path_time = np.mod(cur_time_sec, total_travel_time)
        latitude = float(splev(cur_path_time, spline_reps[0]))
        longitude = float(splev(cur_path_time, spline_reps[1]))
        altitude_msl = float(splev(cur_path_time, spline_reps[2]))

        return (latitude, longitude, altitude_msl)

    def containsPos(self, obst_pos, aerial_pos):
        """Whether the pos is contained within the obstacle's pos.

        Args:
            obst_pos: The position of the obstacle. Use getPosition().
            aerial_pos: The position to test.
        Returns:
            Whether the given position is inside the obstacle.
        """
        dist_to_center = obst_pos.distanceTo(aerial_pos)
        return dist_to_center <= self.sphere_radius

    def evaluateCollisionWithUas(self, uas_telemetry_logs):
        """Evaluates whether the Uas logs indicate a collision.

        Args:
            uas_telemetry_logs: A list of UasTelemetry logs sorted by timestamp
                for which to evaluate.
        Returns:
            Whether a UAS telemetry log reported indicates a collision with the
            obstacle.
        """
        for cur_log in uas_telemetry_logs:
            (lat, lon, alt) = self.getPosition(cur_log.timestamp)
            gpos = GpsPosition()
            gpos.latitude = lat
            gpos.longitude = lon
            apos = AerialPosition()
            apos.gps_position = gpos
            apos.altitude_msl = alt
            if self.containsPos(apos, cur_log.uas_position):
                return True
        return False

    def toJSON(self):
        """Obtain a JSON style representation of object."""
        (latitude, longitude, altitude_msl) = self.getPosition()
        data = {
            'latitude': latitude,
            'longitude': longitude,
            'altitude_msl': altitude_msl,
            'sphere_radius': self.sphere_radius
        }
        return data


class FlyZone(models.Model):
    """An approved area for UAS flight. UAS shall be in at least one zone."""
    # The polygon defining the boundary of the zone.
    boundary_pts = models.ManyToManyField(Waypoint)
    # The minimum altitude of the zone (AGL) in feet
    altitude_msl_min = models.FloatField()
    # The maximum altitude of the zone (AGL) in feet
    altitude_msl_max = models.FloatField()

    def __unicode__(self):
        """Descriptive text for use in displays."""
        boundary_strs = ["%s" % wpt.__unicode__()
                          for wpt in self.boundary_pts.all()]
        boundary_str = ", ".join(boundary_strs)
        return unicode("FlyZone (pk:%d, alt_min:%f, alt_max:%f, "
                       "boundary_pts:[%s])" %
                       (self.pk, self.altitude_msl_min, self.altitude_msl_max,
                        boundary_str))

    def containsPos(self, aerial_pos):
        """Whether the given pos is inside the zone.

        Args:
            aerial_pos: The AerialPosition to test.
        Returns:
            Whether the given position is inside the flight boundary.
        """
        return self.containsManyPos([aerial_pos])[0]

    def containsManyPos(self, aerial_pos_list):
        """Evaluates a list of positions more efficiently than inidividually.

        Args:
            aerial_pos_list: A list of AerialPositions to test.
        Returns:
            A list storing whether each position is inside the boundary.
        """
        # Get boundary points
        ordered_pts = self.boundary_pts.order_by('order')
        path_pts = [[wpt.position.gps_position.latitude,
                     wpt.position.gps_position.longitude]
                    for wpt in ordered_pts]
        # First check enough points to define a polygon
        if len(path_pts) < 3:
            return [False] * len(aerial_pos_list)

        # Create path to use for testing polygon inclusion
        path_pts.append(path_pts[0])
        path = mplpath.Path(np.array(path_pts))

        # Test each aerial position for altitude
        results = list()
        for aerial_pos in aerial_pos_list:
            # Check altitude bounds
            alt = aerial_pos.altitude_msl
            altitude_check = (alt <= self.altitude_msl_max
                              and alt >= self.altitude_msl_min)
            results.append(altitude_check)

        # Create a list of positions to test whether inside polygon
        polygon_test_point_ids = [cur_id
                                  for cur_id in range(len(aerial_pos_list))
                                  if results[cur_id]]
        if len(polygon_test_point_ids) == 0:
            return results
        polygon_test_points = [[aerial_pos_list[cur_id].gps_position.latitude,
                                aerial_pos_list[cur_id].gps_position.longitude]
                               for cur_id in polygon_test_point_ids]

        # Test each point for inside polygon
        polygon_test_results = path.contains_points(
                np.array(polygon_test_points))
        for test_id in range(len(polygon_test_point_ids)):
            cur_id = polygon_test_point_ids[test_id]
            results[cur_id] = (polygon_test_results[test_id] == True)

        return results

    @classmethod
    def evaluateUasOutOfBounds(cls, fly_zones, uas_telemetry_logs):
        """Determines amount of time spent out of bounds.

        Args:
            fly_zones: The list of FlyZone that the UAS must be in.
            uas_telemetry_logs: A list of UasTelemetry logs sorted by timestamp
                which demonstrate the flight of the UAS.
        Returns:
            The floating point total time in seconds spent out of bounds as
            indicated by the telemetry logs.
        """
        # Get the aerial positions for the logs
        aerial_pos_list = [cur_log.uas_position
                           for cur_log in uas_telemetry_logs]
        log_ids_to_process = range(len(aerial_pos_list))

        # Evaluate zones against the logs, eliminating satisfied ones, until
        # only the out of boundary ids remain
        for zone in fly_zones:
            # Stop processing if no ids
            if len(log_ids_to_process) == 0:
                break
            # Evaluate the positions still not satisfied
            cur_positions = [aerial_pos_list[cur_id]
                             for cur_id in log_ids_to_process]
            satisfied_positions = zone.containsManyPos(cur_positions)
            # Retain those which were not satisfied in this pass
            log_ids_to_process = [log_ids_to_process[cur_id]
                                  for cur_id in range(len(log_ids_to_process))
                                  if not satisfied_positions[cur_id]]

        # Positions that remain are out of bound positions, compute total time
        total_time = 0
        for cur_id in log_ids_to_process:
            # Ignore first ID position as no start time for comparison
            if cur_id == 0:
                continue
            # Track time between previous and current out of bounds. This is a
            # simplification of time spent out of bounds.
            cur_log = uas_telemetry_logs[cur_id]
            prev_log = uas_telemetry_logs[cur_id-1]
            time_diff = (cur_log.timestamp - prev_log.timestamp).total_seconds()
            total_time += time_diff

        return total_time


class MissionConfig(models.Model):
    """The details for the active mission. There should only be one."""
    # The home position for use as a reference point. Should be the tents.
    home_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_home_pos")
    # The max distance to a waypoint to consider it satisfied/hit in feet.
    mission_waypoints_dist_max = models.FloatField()
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

    def __unicode__(self):
        """Descriptive text for use in displays."""
        mission_waypoints_str = ", ".join(
                ["%s" % wpt.__unicode__()
                 for wpt in self.mission_waypoints.all()])
        search_grid_str = ", ".join(
                ["%s" % wpt.__unicode__()
                 for wpt in self.search_grid_points.all()])
        emergent_grid_str = ", ".join(
                ["%s" % wpt.__unicode__()
                 for wpt in self.emergent_grid_points.all()])

        return unicode("MissionConfig (pk:%d, home_pos:%s, "
                       "mission_waypoints_dist_max:%f, "
                       "mission_waypoints:[%s], search_grid:[%s], "
                       "emergent_grid:[%s], emergent_lkp:%s, off_axis:%s, "
                       "sric_pos:%s, ir_pos:%s, air_drop_pos:%s)" %
                       (self.pk, self.home_pos.__unicode__(),
                        self.mission_waypoints_dist_max,
                        mission_waypoints_str, search_grid_str,
                        emergent_grid_str,
                        self.emergent_last_known_pos.__unicode__(),
                        self.off_axis_target_pos.__unicode__(),
                        self.sric_pos.__unicode__(),
                        self.ir_target_pos.__unicode__(),
                        self.air_drop_pos.__unicode__()))

    def evaluateUasSatisfiedWaypoints(self, uas_telemetry_logs):
        """Determines whether the UAS satisfied the waypoints.

        Args:
            uas_telemetry_logs: A list of UAS Telemetry logs.
        Returns:
            A list of booleans where each value indicates whether the UAS
            satisfied the waypoint for that index.
        """
        waypoints_satisfied = list()
        waypoints = self.mission_waypoints.order_by('order')
        for waypoint in waypoints:
            satisfied = False
            for uas_log in uas_telemetry_logs:
                distance = uas_log.uas_position.distanceTo(waypoint.position)
                if distance < self.mission_waypoints_dist_max:
                    satisfied = True
                    break
            waypoints_satisfied.append(satisfied)
        return waypoints_satisfied

    def evaluateTeams(self):
        """Evaluates the teams (non admin users) of the competition.

        Returns:
            A map from user to evaluate data. The evaluation data has the
            following map structure:
            {
                'waypoints_satisfied': {
                    id: Boolean,
                }
                'out_of_bounds_time': Seconds spent out of bounds,
                'interop_times': {
                    'server_info': {'min': Value, 'max': Value, 'avg': Value},
                    'obst_info': {'min': Value, 'max': Value, 'avg': Value},
                    'uas_telem': {'min': Value, 'max': Value, 'avg': Value},
                },
                'stationary_obst_collision': {
                    id: Boolean
                },
                'moving_obst_collision': {
                    id: Boolean
                }
            }
        """
        # Get base data for mission
        fly_zones = FlyZone.objects.all()
        stationary_obstacles = StationaryObstacle.objects.all()
        moving_obstacles = MovingObstacle.objects.all()
        # Start a results map from user to evaluation data
        results = dict()
        # Fill in evaluation data for each user except admins
        users = User.objects.all()
        logging.info('Starting team evaluations.')
        for user in users:
            # Ignore admins
            if user.is_superuser:
                continue
            logging.info('Evaluation starting for user: %s.' % user.username)
            # Start the evaluation data structure
            eval_data = results.setdefault(user, dict())
            # Get the relevant logs for the user
            server_info_logs = ServerInfoAccessLog.getAccessLogForUser(user)
            obstacle_logs = ObstacleAccessLog.getAccessLogForUser(user)
            uas_telemetry_logs = UasTelemetry.getAccessLogForUser(user)
            flight_periods = TakeoffOrLandingEvent.getFlightPeriodsForUser(
                    user)
            # Determine if the uas hit the waypoints
            waypoints = self.evaluateUasSatisfiedWaypoints(uas_telemetry_logs)
            waypoints_keyed = dict()
            for wpt_id in xrange(len(waypoints)):
                waypoints_keyed[wpt_id+1] = waypoints[wpt_id]
            eval_data['waypoints_satisfied'] = waypoints_keyed
            # Determine if the uas went out of bounds 
            out_of_bounds_time = FlyZone.evaluateUasOutOfBounds(
                    fly_zones, uas_telemetry_logs)
            eval_data['out_of_bounds_time'] = out_of_bounds_time
            # Determine interop rates
            interop_times = eval_data.setdefault('interop_times', dict())
            server_info_times = ServerInfoAccessLog.getAccessLogRates(
                    flight_periods,
                    ServerInfoAccessLog.getAccessLogForUserByTimePeriod(
                        server_info_logs, flight_periods)
                    )
            obstacle_times = ObstacleAccessLog.getAccessLogRates(
                    flight_periods,
                    ObstacleAccessLog.getAccessLogForUserByTimePeriod(
                        obstacle_logs, flight_periods)
                    )
            uas_telemetry_times = UasTelemetry.getAccessLogRates(
                    flight_periods,
                    UasTelemetry.getAccessLogForUserByTimePeriod(
                        uas_telemetry_logs, flight_periods)
                    )
            interop_times['server_info'] = {
                    'min': server_info_times[0],
                    'max': server_info_times[1],
                    'avg': server_info_times[2]
            }
            interop_times['obst_info'] = {
                    'min': obstacle_times[0],
                    'max': obstacle_times[1],
                    'avg': obstacle_times[2]
            }
            interop_times['uas_telem'] = {
                    'min': uas_telemetry_times[0],
                    'max': uas_telemetry_times[1],
                    'avg': uas_telemetry_times[2]
            }
            # Determine collisions with stationary and moving obstacles
            stationary_collisions = eval_data.setdefault(
                    'stationary_obst_collision', dict())
            for obst in stationary_obstacles:
                collision = obst.evaluateCollisionWithUas(uas_telemetry_logs)
                stationary_collisions[obst.pk] = collision
            moving_collisions = eval_data.setdefault(
                    'moving_obst_collision', dict())
            for obst in moving_obstacles:
                collision = obst.evaluateCollisionWithUas(uas_telemetry_logs)
                moving_collisions[obst.pk] = collision
        return results

