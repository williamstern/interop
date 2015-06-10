"""Mission configuration model."""

import logging
from auvsi_suas.patches.simplekml_patch import Color
from auvsi_suas.patches.simplekml_patch import AltitudeMode
from fly_zone import FlyZone
from gps_position import GpsPosition
from moving_obstacle import MovingObstacle
from obstacle_access_log import ObstacleAccessLog
from server_info_access_log import ServerInfoAccessLog
from stationary_obstacle import StationaryObstacle
from takeoff_or_landing_event import TakeoffOrLandingEvent
from uas_telemetry import UasTelemetry
from waypoint import Waypoint
from django.contrib.auth.models import User
from django.db import models


# Logging for the module
logger = logging.getLogger(__name__)


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
    # The last known position of the emergent target
    emergent_last_known_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_emergent_last_known_pos")
    # Off-axis target position
    off_axis_target_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_off_axis_target_pos")
    # The SRIC position
    sric_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_sric_pos")
    # The IR primary target position
    ir_primary_target_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_ir_primary_target_pos")
    # The IR secondary target position
    ir_secondary_target_pos = models.ForeignKey(
            GpsPosition, related_name="missionconfig_ir_secondary_target_pos")
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

        return unicode("MissionConfig (pk:%s, home_pos:%s, "
                       "mission_waypoints_dist_max:%s, "
                       "mission_waypoints:[%s], search_grid:[%s], "
                       "emergent_lkp:%s, off_axis:%s, "
                       "sric_pos:%s, ir_primary_pos:%s, ir_secondary_pos:%s, "
                       "air_drop_pos:%s)" %
                       (str(self.pk), self.home_pos.__unicode__(),
                        str(self.mission_waypoints_dist_max),
                        mission_waypoints_str, search_grid_str,
                        self.emergent_last_known_pos.__unicode__(),
                        self.off_axis_target_pos.__unicode__(),
                        self.sric_pos.__unicode__(),
                        self.ir_primary_target_pos.__unicode__(),
                        self.ir_secondary_target_pos.__unicode__(),
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
        logger.info('Starting team evaluations.')
        for user in users:
            # Ignore admins
            if user.is_superuser:
                continue
            logger.info('Evaluation starting for user: %s.' % user.username)
            # Start the evaluation data structure
            eval_data = results.setdefault(user, dict())
            # Get the relevant logs for the user
            server_info_logs = ServerInfoAccessLog.getAccessLogForUser(user)
            obstacle_logs = ObstacleAccessLog.getAccessLogForUser(user)
            uas_telemetry_logs = UasTelemetry.getAccessLogForUser(user)
            flight_periods = TakeoffOrLandingEvent.getFlightPeriodsForUser(user)
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

    def toJSON(self):
        """Return a dict, for conversion to JSON."""
        ret = {
            "id": self.pk,
            "home_pos": {
                "latitude": self.home_pos.latitude,
                "longitude": self.home_pos.longitude,
            },
            "mission_waypoints_dist_max": self.mission_waypoints_dist_max,
            "mission_waypoints": [], # Filled in below
            "search_grid_points": [], # Filled in below
            "emergent_last_known_pos": {
                "latitude": self.emergent_last_known_pos.latitude,
                "longitude": self.emergent_last_known_pos.longitude,
            },
            "off_axis_target_pos": {
                "latitude": self.off_axis_target_pos.latitude,
                "longitude": self.off_axis_target_pos.longitude,
            },
            "sric_pos": {
                "latitude": self.sric_pos.latitude,
                "longitude": self.sric_pos.longitude,
            },
            "ir_primary_target_pos": {
                "latitude": self.ir_primary_target_pos.latitude,
                "longitude": self.ir_primary_target_pos.longitude,
            },
            "ir_secondary_target_pos": {
                "latitude": self.ir_secondary_target_pos.latitude,
                "longitude": self.ir_secondary_target_pos.longitude,
            },
            "air_drop_pos": {
                "latitude": self.air_drop_pos.latitude,
                "longitude": self.air_drop_pos.longitude,
            },
        }

        for waypoint in self.mission_waypoints.all():
            ret['mission_waypoints'].append({
                "id": waypoint.pk,
                "latitude": waypoint.position.gps_position.latitude,
                "longitude": waypoint.position.gps_position.longitude,
                "altitude_msl": waypoint.position.altitude_msl,
                "order": waypoint.order,
            })

        for point in self.search_grid_points.all():
            ret['search_grid_points'].append({
                "id": point.pk,
                "latitude": point.position.gps_position.latitude,
                "longitude": point.position.gps_position.longitude,
                "altitude_msl": point.position.altitude_msl,
                "order": point.order,
            })

        return ret

    @classmethod
    def kml(cls, kml):
        """
        Appends kml nodes describing the mission configurations.

        Args:
            kml: A simpleKML Container to which the flight data will be added
        Returns:
            None
        """
        for mission_number, mission in enumerate(MissionConfig.objects.all()):
            mission_name = 'Mission {}'.format(mission_number)
            kml_folder = kml.newfolder(name=mission_name)

            # Static Points
            locations = {
                'Home Position': mission.home_pos,
                'Emergent LKP': mission.emergent_last_known_pos,
                'Off Axis': mission.off_axis_target_pos,
                'SRIC': mission.sric_pos,
                'IR Primary': mission.ir_primary_target_pos,
                'IR Secondary': mission.ir_secondary_target_pos,
                'Air Drop': mission.air_drop_pos,
            }
            for key, point in locations.iteritems():
                coord = (point.longitude, point.latitude)
                kml_folder.newpoint(name=key, coords=[coord])

            # Waypoints
            waypoints_folder = kml_folder.newfolder(name='Flight Area')
            linestring = waypoints_folder.newlinestring(name="A Line")
            waypoints = []
            for waypoint in mission.mission_waypoints.all():
                coord = waypoint.position.gps_position
                waypoints.append((coord.longitude, coord.latitude, waypoint.position.altitude_msl))
            linestring.coords = waypoints

            # Waypoints Style
            linestring.altitudemode = AltitudeMode.absolute
            linestring.extrude = 1
            linestring.style.linestyle.color = Color.black
            linestring.style.polystyle.color = Color.changealphaint(100, Color.green)

            # Waypoints Points
            for n, point in enumerate(waypoints):
                wp = waypoints_folder.newpoint(name=str(n), coords=[point])
                wp.altitudemode = AltitudeMode.absolute
                wp.extrude = 1
                wp.visibility = False

            # Flight Area
            flight_area_folder = kml_folder.newfolder(name='Flight Area')
            pol = flight_area_folder.newpolygon(name='Flight Area')
            search_area = []
            for point in mission.search_grid_points.all():
                coord = point.position.gps_position
                search_area.append((coord.longitude, coord.latitude, point.position.altitude_msl))
            search_area.append(search_area[0])
            pol.outerboundaryis = search_area

            # Flight Area Style
            pol.style.linestyle.color = Color.red
            pol.style.linestyle.width = 2
            pol.style.polystyle.color = Color.changealphaint(50, Color.green)

            # Flight Area Points
            for n, point in enumerate(search_area[:-1]):
                wp = flight_area_folder.newpoint(name=str(n), coords=[point])
                wp.visibility = False
