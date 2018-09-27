"""Mission configuration model."""

import datetime
import itertools
import logging
from auvsi_suas.models import units
from auvsi_suas.models.fly_zone import FlyZone
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.mission_clock_event import MissionClockEvent
from auvsi_suas.models.moving_obstacle import MovingObstacle
from auvsi_suas.models.odlc import Odlc
from auvsi_suas.models.odlc import OdlcEvaluator
from auvsi_suas.models.stationary_obstacle import StationaryObstacle
from auvsi_suas.models.takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.models.time_period import TimePeriod
from auvsi_suas.models.uas_telemetry import UasTelemetry
from auvsi_suas.models.waypoint import Waypoint
from auvsi_suas.patches.simplekml_patch import AltitudeMode
from auvsi_suas.patches.simplekml_patch import Color
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class MissionConfig(models.Model):
    """The details for the mission.

    Attributes:
        is_active: Whether the mission is active. Only one mission can be
            active at a time.
        home_pos: The home position for use as a reference point. Should be the
            tents.
        fly_zones: Valid areas for the UAS to fly.
        mission_waypoints: The waypoints that define the mission waypoint path
        search_grid_points: The polygon that defines the search grid.
        odlcs: The judge created objects for detection.
        emergent_last_known_pos: The last known position of the emergent object.
        off_axis_odlc_pos: Off-axis object position.
        air_drop_pos: The air drop position.
        stationary_obstacles: The stationary obstacles.
        moving_obstacles: The moving obstacles.
    """
    is_active = models.BooleanField(default=False)
    home_pos = models.ForeignKey(
        GpsPosition,
        related_name="missionconfig_home_pos",
        on_delete=models.CASCADE)
    fly_zones = models.ManyToManyField(FlyZone)
    mission_waypoints = models.ManyToManyField(
        Waypoint, related_name='missionconfig_mission_waypoints')
    search_grid_points = models.ManyToManyField(
        Waypoint, related_name='missionconfig_search_grid_points')
    odlcs = models.ManyToManyField(Odlc, related_name='missionconfig_odlc')
    emergent_last_known_pos = models.ForeignKey(
        GpsPosition,
        related_name='missionconfig_emergent_last_known_pos',
        on_delete=models.CASCADE)
    off_axis_odlc_pos = models.ForeignKey(
        GpsPosition,
        related_name='missionconfig_off_axis_odlc_pos',
        on_delete=models.CASCADE)
    air_drop_pos = models.ForeignKey(
        GpsPosition,
        related_name='missionconfig_air_drop_pos',
        on_delete=models.CASCADE)
    stationary_obstacles = models.ManyToManyField(StationaryObstacle)
    moving_obstacles = models.ManyToManyField(MovingObstacle)

    def json(self, is_superuser):
        """Return a dict, for conversion to JSON."""
        ret = {
            'id': self.pk,
            'active': self.is_active,
            'home_pos': {
                'latitude': self.home_pos.latitude,
                'longitude': self.home_pos.longitude,
            },
            "fly_zones": [],  # Filled in below
            "mission_waypoints": [],  # Filled in below
            "search_grid_points": [],  # Filled in below
            'off_axis_odlc_pos': {
                'latitude': self.off_axis_odlc_pos.latitude,
                'longitude': self.off_axis_odlc_pos.longitude,
            },
            "emergent_last_known_pos": {
                "latitude": self.emergent_last_known_pos.latitude,
                "longitude": self.emergent_last_known_pos.longitude,
            },
            'air_drop_pos': {
                'latitude': self.air_drop_pos.latitude,
                'longitude': self.air_drop_pos.longitude,
            },
        }
        for zone in self.fly_zones.all():
            pts = [{
                "latitude": bpt.position.gps_position.latitude,
                "longitude": bpt.position.gps_position.longitude,
                "order": bpt.order
            } for bpt in zone.boundary_pts.order_by('order')]
            ret['fly_zones'].append({
                "boundary_pts": pts,
                "altitude_msl_min": zone.altitude_msl_min,
                "altitude_msl_max": zone.altitude_msl_max
            })
        for waypoint in self.mission_waypoints.order_by('order'):
            ret['mission_waypoints'].append({
                'order':
                waypoint.order,
                'latitude':
                waypoint.position.gps_position.latitude,
                'longitude':
                waypoint.position.gps_position.longitude,
                'altitude_msl':
                waypoint.position.altitude_msl,
            })
        for point in self.search_grid_points.order_by('order'):
            ret['search_grid_points'].append({
                'order':
                point.order,
                'latitude':
                point.position.gps_position.latitude,
                'longitude':
                point.position.gps_position.longitude,
                'altitude_msl':
                point.position.altitude_msl,
            })
        if not is_superuser:
            return ret

        ret.update({
            'stationary_obstacles': [],  # Filled in below
            'moving_obstacles': [],  # Filled in below
        })
        for obst in self.stationary_obstacles.all():
            ret['stationary_obstacles'].append({
                'latitude':
                obst.gps_position.latitude,
                'longitude':
                obst.gps_position.longitude,
                'cylinder_radius':
                obst.cylinder_radius,
                'cylinder_height':
                obst.cylinder_height,
            })
        for obst in self.moving_obstacles.all():
            ret['moving_obstacles'].append({
                'speed_avg': obst.speed_avg,
                'sphere_radius': obst.sphere_radius,
            })
        return ret

    @classmethod
    def kml_all(cls, kml, kml_doc, missions=None):
        """
        Appends kml nodes describing all mission configurations.

        Args:
            kml: A simpleKML Container to which the mission data will be added
            kml_doc: The simpleKML Document to which schemas will be added
            missions: Optional list of mission for which to generate KML. If
                None, it will use all missions.
        """
        if not missions:
            missions = MissionConfig.objects.all()

        for mission in missions:
            mission.kml(kml, kml_doc)

    def kml(self, kml, kml_doc):
        """
        Appends kml nodes describing this mission configurations.

        Args:
            kml: A simpleKML Container to which the mission data will be added
            kml_doc: The simpleKML Document to which schemas will be added
        """
        mission_name = 'Mission {}'.format(self.pk)
        kml_folder = kml.newfolder(name=mission_name)

        # Static Points
        locations = {
            'Home Position': self.home_pos,
            'Emergent LKP': self.emergent_last_known_pos,
            'Off Axis': self.off_axis_odlc_pos,
            'Air Drop': self.air_drop_pos,
        }
        for key, point in locations.items():
            gps = (point.longitude, point.latitude)
            wp = kml_folder.newpoint(name=key, coords=[gps])
            wp.description = str(point)

        # Waypoints
        waypoints_folder = kml_folder.newfolder(name='Waypoints')
        linestring = waypoints_folder.newlinestring(name='Waypoints')
        waypoints = []
        waypoint_num = 1
        for waypoint in self.mission_waypoints.order_by('order'):
            gps = waypoint.position.gps_position
            coord = (gps.longitude, gps.latitude,
                     units.feet_to_meters(waypoint.position.altitude_msl))
            waypoints.append(coord)

            # Add waypoint marker
            wp = waypoints_folder.newpoint(
                name=str(waypoint_num), coords=[coord])
            wp.description = str(waypoint)
            wp.altitudemode = AltitudeMode.absolute
            wp.extrude = 1
            wp.visibility = False
            waypoint_num += 1
        linestring.coords = waypoints

        # Waypoints Style
        linestring.altitudemode = AltitudeMode.absolute
        linestring.extrude = 1
        linestring.style.linestyle.color = Color.black
        linestring.style.polystyle.color = Color.changealphaint(
            100, Color.green)

        # Search Area
        search_area_folder = kml_folder.newfolder(name='Search Area')
        search_area = []
        search_area_num = 1
        for point in self.search_grid_points.order_by('order'):
            gps = point.position.gps_position
            coord = (gps.longitude, gps.latitude,
                     units.feet_to_meters(point.position.altitude_msl))
            search_area.append(coord)

            # Add boundary marker
            wp = search_area_folder.newpoint(
                name=str(search_area_num), coords=[coord])
            wp.description = str(point)
            wp.visibility = False
            search_area_num += 1
        if search_area:
            # Create search area polygon.
            pol = search_area_folder.newpolygon(name='Search Area')
            search_area.append(search_area[0])
            pol.outerboundaryis = search_area
            # Search Area Style.
            pol.style.linestyle.color = Color.black
            pol.style.linestyle.width = 2
            pol.style.polystyle.color = Color.changealphaint(50, Color.blue)

        # Stationary Obstacles.
        stationary_obstacles_folder = kml_folder.newfolder(
            name='Stationary Obstacles')
        # TODO: Implement

        # Moving Obstacles.
        users = User.objects.all()
        moving_obstacle_periods = []
        for user in users:
            moving_obstacle_periods.extend(TakeoffOrLandingEvent.flights(user))
        moving_obstacles_folder = kml_folder.newfolder(name='Moving Obstacles')
        for obstacle in self.moving_obstacles.all():
            obstacle.kml(moving_obstacle_periods, moving_obstacles_folder,
                         kml_doc)


@admin.register(MissionConfig)
class MissionConfigModelAdmin(admin.ModelAdmin):
    raw_id_fields = ("home_pos", "emergent_last_known_pos",
                     "off_axis_odlc_pos", "air_drop_pos")
    filter_horizontal = ("fly_zones", "mission_waypoints",
                         "search_grid_points", "odlcs", "stationary_obstacles",
                         "moving_obstacles")
    list_display = ('is_active', 'home_pos')
