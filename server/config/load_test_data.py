#!/usr/bin/env python3
"""Installs test data into server."""

# Add server to Python path.
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Setup Django.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import logging
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.fly_zone import FlyZone
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.mission_config import MissionConfig
from auvsi_suas.models.odlc import Odlc
from auvsi_suas.models.stationary_obstacle import StationaryObstacle
from auvsi_suas.models.waypoint import Waypoint
from auvsi_suas.proto import interop_api_pb2
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


def main():
    logger.info('Loading test data.')

    testadmin = get_user_model().objects.create_superuser(
        username='testadmin', password='testpass', email='test@test.com')
    testuser = get_user_model().objects.create_user(
        username='testuser', password='testpass', email='test@test.com')

    mission = MissionConfig()

    gpos = GpsPosition(latitude=38.145103, longitude=-76.427856)
    gpos.save()
    mission.home_pos = gpos

    gpos = GpsPosition(latitude=38.145111, longitude=-76.427861)
    gpos.save()
    mission.emergent_last_known_pos = gpos

    gpos = GpsPosition(latitude=38.145111, longitude=-76.427861)
    gpos.save()
    mission.off_axis_odlc_pos = gpos

    gpos = GpsPosition(latitude=38.1458416666667, longitude=-76.426375)
    gpos.save()
    mission.air_drop_pos = gpos

    # All foreign keys must be defined before the first save.
    # All many-to-many must be defined after the first save.
    mission.save()

    bounds = FlyZone(altitude_msl_min=100, altitude_msl_max=750)
    bounds.save()
    # yapf: disable
    pts = [(38.1462694444444, -76.4281638888889),
           (38.1516250000000, -76.4286833333333),
           (38.1518888888889, -76.4314666666667),
           (38.1505944444444, -76.4353611111111),
           (38.1475666666667, -76.4323416666667),
           (38.1446666666667, -76.4329472222222),
           (38.1432555555556, -76.4347666666667),
           (38.1404638888889, -76.4326361111111),
           (38.1407194444444, -76.4260138888889),
           (38.1437611111111, -76.4212055555556),
           (38.1473472222222, -76.4232111111111),
           (38.1461305555556, -76.4266527777778)]
    # yapf: enable
    for ix, (lat, lon) in enumerate(pts):
        gpos = GpsPosition(latitude=lat, longitude=lon)
        gpos.save()
        apos = AerialPosition(gps_position=gpos, altitude_msl=0)
        apos.save()
        wpt = Waypoint(position=apos, order=ix + 1)
        wpt.save()
        bounds.boundary_pts.add(wpt)
    bounds.save()
    mission.fly_zones.add(bounds)

    # yapf: disable
    pts = [(38.146689, -76.426475, 150,
            750), (38.142914, -76.430297, 300,
                   300), (38.149504, -76.433110, 100,
                          750), (38.148711, -76.429061, 300, 750),
           (38.144203, -76.426155, 50, 400), (38.146003, -76.430733, 225, 500)]
    # yapf: enable
    for lat, lon, radius, height in pts:
        gpos = GpsPosition(latitude=lat, longitude=lon)
        gpos.save()
        obst = StationaryObstacle(
            gps_position=gpos, cylinder_radius=radius, cylinder_height=height)
        obst.save()
        mission.stationary_obstacles.add(obst)

    # yapf: disable
    pts = [(38.1446916666667, -76.4279944444445, 200),
           (38.1461944444444, -76.4237138888889, 300),
           (38.1438972222222, -76.4225500000000, 400),
           (38.1417722222222, -76.4251083333333, 400),
           (38.1453500000000, -76.4286750000000, 300),
           (38.1508972222222, -76.4292972222222, 300),
           (38.1514944444444, -76.4313833333333, 300),
           (38.1505333333333, -76.4341750000000, 300),
           (38.1479472222222, -76.4316055555556, 200),
           (38.1443333333333, -76.4322888888889, 200),
           (38.1433166666667, -76.4337111111111, 300),
           (38.1410944444444, -76.4321555555556, 400),
           (38.1415777777778, -76.4252472222222, 400),
           (38.1446083333333, -76.4282527777778, 200)]
    # yapf: enable
    for ix, (lat, lon, alt) in enumerate(pts):
        gpos = GpsPosition(latitude=lat, longitude=lon)
        gpos.save()
        apos = AerialPosition(gps_position=gpos, altitude_msl=alt)
        apos.save()
        wpt = Waypoint(position=apos, order=ix + 1)
        wpt.save()
        mission.mission_waypoints.add(wpt)

    # yapf: disable
    pts = [(38.1444444444444, -76.4280916666667),
           (38.1459444444444, -76.4237944444445),
           (38.1439305555556, -76.4227444444444),
           (38.1417138888889, -76.4253805555556),
           (38.1412111111111, -76.4322361111111),
           (38.1431055555556, -76.4335972222222),
           (38.1441805555556, -76.4320111111111),
           (38.1452611111111, -76.4289194444444),
           (38.1444444444444, -76.4280916666667)]
    # yapf: enable
    for ix, (lat, lon) in enumerate(pts):
        gpos = GpsPosition(latitude=lat, longitude=lon)
        gpos.save()
        apos = AerialPosition(gps_position=gpos, altitude_msl=0)
        apos.save()
        wpt = Waypoint(position=apos, order=ix + 1)
        wpt.save()
        mission.search_grid_points.add(wpt)

    gpos = GpsPosition(latitude=38.143844, longitude=-76.426469)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.N,
        shape=interop_api_pb2.Odlc.STAR,
        shape_color=interop_api_pb2.Odlc.RED,
        alphanumeric='A',
        alphanumeric_color=interop_api_pb2.Odlc.WHITE)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.141872, longitude=-76.426183)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.NE,
        shape=interop_api_pb2.Odlc.CROSS,
        shape_color=interop_api_pb2.Odlc.BLUE,
        alphanumeric='I',
        alphanumeric_color=interop_api_pb2.Odlc.BLACK)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.142828, longitude=-76.427644)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.E,
        shape=interop_api_pb2.Odlc.QUARTER_CIRCLE,
        shape_color=interop_api_pb2.Odlc.YELLOW,
        alphanumeric='R',
        alphanumeric_color=interop_api_pb2.Odlc.ORANGE)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.144925, longitude=-76.425100)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.SE,
        shape=interop_api_pb2.Odlc.CIRCLE,
        shape_color=interop_api_pb2.Odlc.BROWN,
        alphanumeric='V',
        alphanumeric_color=interop_api_pb2.Odlc.RED)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.146747, longitude=-76.422131)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.S,
        shape=interop_api_pb2.Odlc.TRAPEZOID,
        shape_color=interop_api_pb2.Odlc.WHITE,
        alphanumeric='E',
        alphanumeric_color=interop_api_pb2.Odlc.GRAY)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.144097, longitude=-76.431089)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.SW,
        shape=interop_api_pb2.Odlc.SQUARE,
        shape_color=interop_api_pb2.Odlc.GREEN,
        alphanumeric='H',
        alphanumeric_color=interop_api_pb2.Odlc.BLUE)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.144878, longitude=-76.423681)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.W,
        shape=interop_api_pb2.Odlc.RECTANGLE,
        shape_color=interop_api_pb2.Odlc.PURPLE,
        alphanumeric='I',
        alphanumeric_color=interop_api_pb2.Odlc.GREEN)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.142819, longitude=-76.432375)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.NW,
        shape=interop_api_pb2.Odlc.SEMICIRCLE,
        shape_color=interop_api_pb2.Odlc.ORANGE,
        alphanumeric='C',
        alphanumeric_color=interop_api_pb2.Odlc.YELLOW)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.141639, longitude=-76.429347)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.N,
        shape=interop_api_pb2.Odlc.TRIANGLE,
        shape_color=interop_api_pb2.Odlc.BLACK,
        alphanumeric='L',
        alphanumeric_color=interop_api_pb2.Odlc.PURPLE)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.142478, longitude=-76.424967)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.STANDARD,
        location=gpos,
        orientation=interop_api_pb2.Odlc.NE,
        shape=interop_api_pb2.Odlc.PENTAGON,
        shape_color=interop_api_pb2.Odlc.GRAY,
        alphanumeric='E',
        alphanumeric_color=interop_api_pb2.Odlc.BROWN)
    odlc.save()
    mission.odlcs.add(odlc)

    gpos = GpsPosition(latitude=38.143411, longitude=-76.424489)
    gpos.save()
    odlc = Odlc(
        mission=mission,
        user=testadmin,
        odlc_type=interop_api_pb2.Odlc.EMERGENT,
        location=gpos,
        description='Randy the backpacker.')
    odlc.save()
    mission.odlcs.add(odlc)

    mission.save()


if __name__ == "__main__":
    main()
