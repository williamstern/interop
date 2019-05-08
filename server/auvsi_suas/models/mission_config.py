"""Mission configuration model."""

import logging
import math
import numpy as np
from auvsi_suas.models import distance
from auvsi_suas.models import units
from auvsi_suas.models.fly_zone import FlyZone
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.odlc import Odlc
from auvsi_suas.models.stationary_obstacle import StationaryObstacle
from auvsi_suas.models.takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.models.waypoint import Waypoint
from auvsi_suas.patches.simplekml_patch import AltitudeMode
from auvsi_suas.patches.simplekml_patch import Color
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)

KML_HOME_ICON = 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png'
KML_WAYPOINT_ICON = 'http://maps.google.com/mapfiles/kml/paddle/blu-circle.png'
KML_ODLC_ICON = 'http://maps.google.com/mapfiles/kml/shapes/donut.png'
KML_DROP_ICON = 'http://maps.google.com/mapfiles/kml/shapes/target.png'
KML_OBST_NUM_POINTS = 20


class MissionConfig(models.Model):
    """The details for the mission.

    Attributes:
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
    """
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

        # Flight boundaries.
        fly_zone_folder = kml_folder.newfolder(name='Fly Zones')
        for flyzone in self.fly_zones.all():
            flyzone.kml(fly_zone_folder)

        # Static points.
        locations = [
            ('Home', self.home_pos, KML_HOME_ICON),
            ('Emergent LKP', self.emergent_last_known_pos, KML_ODLC_ICON),
            ('Off Axis', self.off_axis_odlc_pos, KML_ODLC_ICON),
            ('Air Drop', self.air_drop_pos, KML_DROP_ICON),
        ]
        for key, point, icon in locations:
            gps = (point.longitude, point.latitude)
            p = kml_folder.newpoint(name=key, coords=[gps])
            p.iconstyle.icon.href = icon
            p.description = str(point)

        # ODLCs.
        oldc_folder = kml_folder.newfolder(name='ODLCs')
        for odlc in self.odlcs.all():
            name = 'ODLC %d' % odlc.pk
            gps = (odlc.location.longitude, odlc.location.latitude)
            p = oldc_folder.newpoint(name=name, coords=[gps])
            p.iconstyle.icon.href = KML_ODLC_ICON
            p.description = name

        # Waypoints
        waypoints_folder = kml_folder.newfolder(name='Waypoints')
        linestring = waypoints_folder.newlinestring(name='Waypoints')
        waypoints = []
        for i, waypoint in enumerate(self.mission_waypoints.order_by('order')):
            gps = waypoint.position.gps_position
            coord = (gps.longitude, gps.latitude,
                     units.feet_to_meters(waypoint.position.altitude_msl))
            waypoints.append(coord)

            # Add waypoint marker
            p = waypoints_folder.newpoint(
                name='Waypoint %d' % (i + 1), coords=[coord])
            p.iconstyle.icon.href = KML_WAYPOINT_ICON
            p.description = str(waypoint)
            p.altitudemode = AltitudeMode.absolute
            p.extrude = 1
        linestring.coords = waypoints
        linestring.altitudemode = AltitudeMode.absolute
        linestring.extrude = 1
        linestring.style.linestyle.color = Color.green
        linestring.style.polystyle.color = Color.changealphaint(
            100, Color.green)

        # Search Area
        search_area = []
        for point in self.search_grid_points.order_by('order'):
            gps = point.position.gps_position
            coord = (gps.longitude, gps.latitude,
                     units.feet_to_meters(point.position.altitude_msl))
            search_area.append(coord)
        if search_area:
            search_area.append(search_area[0])
            pol = kml_folder.newpolygon(name='Search Area')
            pol.outerboundaryis = search_area
            pol.style.linestyle.color = Color.blue
            pol.style.linestyle.width = 2
            pol.style.polystyle.color = Color.changealphaint(50, Color.blue)

        # Stationary Obstacles.
        stationary_obstacles_folder = kml_folder.newfolder(
            name='Stationary Obstacles')
        for obst in self.stationary_obstacles.all():
            gpos = obst.gps_position
            zone, north = distance.utm_zone(gpos.latitude, gpos.longitude)
            proj = distance.proj_utm(zone, north)
            cx, cy = proj(gpos.longitude, gpos.latitude)
            rm = units.feet_to_meters(obst.cylinder_radius)
            hm = units.feet_to_meters(obst.cylinder_height)
            obst_points = []
            for angle in np.linspace(0, 2 * math.pi, num=KML_OBST_NUM_POINTS):
                px = cx + rm * math.cos(angle)
                py = cy + rm * math.sin(angle)
                lon, lat = proj(px, py, inverse=True)
                obst_points.append((lon, lat, hm))
            pol = stationary_obstacles_folder.newpolygon(
                name='Obstacle %d' % obst.pk)
            pol.outerboundaryis = obst_points
            pol.altitudemode = AltitudeMode.absolute
            pol.extrude = 1
            pol.style.linestyle.color = Color.yellow
            pol.style.linestyle.width = 2
            pol.style.polystyle.color = Color.changealphaint(50, Color.yellow)


@admin.register(MissionConfig)
class MissionConfigModelAdmin(admin.ModelAdmin):
    raw_id_fields = ("home_pos", "emergent_last_known_pos",
                     "off_axis_odlc_pos", "air_drop_pos")
    filter_horizontal = ("fly_zones", "mission_waypoints",
                         "search_grid_points", "odlcs", "stationary_obstacles")
    list_display = ('home_pos', )
