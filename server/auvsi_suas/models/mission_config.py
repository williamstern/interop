"""Mission configuration model."""

import logging
from auvsi_suas.models.fly_zone import FlyZone
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.odlc import Odlc
from auvsi_suas.models.stationary_obstacle import StationaryObstacle
from auvsi_suas.models.waypoint import Waypoint
from django.contrib import admin
from django.db import models

logger = logging.getLogger(__name__)


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

    def __str__(self):
        return 'Mission %d' % self.pk


@admin.register(MissionConfig)
class MissionConfigModelAdmin(admin.ModelAdmin):
    raw_id_fields = ("home_pos", "emergent_last_known_pos",
                     "off_axis_odlc_pos", "air_drop_pos")
    filter_horizontal = ("fly_zones", "mission_waypoints",
                         "search_grid_points", "odlcs", "stationary_obstacles")
    list_display = ('home_pos', )
