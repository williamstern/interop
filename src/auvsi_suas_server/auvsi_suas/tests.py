import datetime
import time
import json
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import shutil
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import AccessLog
from auvsi_suas.models import FlyZone
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import haversine
from auvsi_suas.models import kilometersToFeet
from auvsi_suas.models import knotsToFeetPerSecond
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import ObstacleAccessLog
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from auvsi_suas.models import StationaryObstacle
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import Waypoint
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone


# Whether to perform tests which require plotting (window access)
TEST_ENABLE_PLOTTING = False

# Whether to perform load tests
TEST_ENABLE_LOADTEST = False

# The loadtest parameters
OP_RATE_T = 10.0
OP_RATE_HZ = 10.0
OP_RATE_PROCS = 4.0
OP_RATE_SAFETY = 1.5
OP_RATE_THRESH = OP_RATE_HZ * OP_RATE_SAFETY
OP_RATE_INDIV_THRESH = OP_RATE_THRESH * OP_RATE_PROCS

TESTDATA_COMPETITION_DIST = [
    (-76.428709, 38.145306, -76.426375, 38.146146, 0.22446),
    (-76.428537, 38.145399, -76.427818, 38.144686, 0.10045),
    (-76.434261, 38.142471, -76.418876, 38.147838, 1.46914)
]

# [(user, [(timestamp, in_air)], [(time_start, time_end)]]
TESTDATA_TAKEOFFORLANDINGEVENT = [
    ('no_logs',
        [],
        []),
    ('forgot_takeoff',
        [(0.0, False)],
        [(None, 0.0)]),
    ('forgot_landing',
        [(0.0, True)],
        [(0.0, None)]),
    ('single_flight',
        [(0.0, True), (100.0, False)],
        [(0.0, 100.0)]),
    ('multi_flight',
        [(0.0, True), (100.0, False), (150.0, True), (200.0, False)],
        [(0.0, 100.0), (150.0, 200.0)]),
    ('multi_with_double_forget',
        [(0.0, False), (1.0, True), (2.0, False), (3.0, True)],
        [(None, 0.0), (1.0, 2.0), (3.0, None)]),
    ('missing_inbetween_log',
        [(0.0, True), (1.0, False), (2.0, False), (3.0, True), (4.0, False)],
        [(0.0, 1.0), (3.0, 4.0)]),
]

# (lat, lon, rad, height)
TESTDATA_STATOBST_CONTAINSPOS_OBJ = (-76, 38, 100, 200)
# (lat, lon, alt)
TESTDATA_STATOBST_CONTAINSPOS_INSIDE = [
    (-76, 38, 0),
    (-76, 38, 200),
    (-76.0002, 38, 100),
    (-76, 38.0003, 100)
]
TESTDATA_STATOBST_CONTAINSPOS_OUTSIDE = [
    (-76, 38, -1),
    (-76, 38, 201),
    (-76.0003, 38, 100),
    (-76, 38.004, 100)
]

TESTDATA_STATOBST_EVALCOLLISION = (
    # Cylinder position
    (-76, 38, 100, 100),
    # Inside positions
    [(-76, 38, 50),
     (-76, 38, 0),
     (-76, 38, 100),
     (-76.0001, 38.0001, 0),
     (-76.0001, 38.0001, 100)],
    # Outside positions
    [(-76.001, 38, 50),
     (-76, 38.002, 50),
     (-76, 38, -1),
     (-76, 38, 101)]
)

# (lat, lon, rad, alt)
TESTDATA_MOVOBST_CONTAINSPOS_OBJ = (-76, 38, 100, 200)
# (lat, lon, alt)
TESTDATA_MOVOBST_CONTAINSPOS_INSIDE = [
    (-76, 38, 100),
    (-76, 38, 300),
    (-76.0002, 38, 200),
    (-76, 38.0003, 200)
]
TESTDATA_MOVOBST_CONTAINSPOS_OUTSIDE = [
    (-76, 38, 99),
    (-76, 38, 301),
    (-76.0003, 38, 200),
    (-76, 38.004, 200)
]

TESTDATA_MOVOBST_PATHS = [
    # Test 2 points
    [(38.142233, -76.434082, 300),
     (38.141878, -76.425198, 700)],
    # Test 3 points
    [(38.142233, -76.434082, 300),
     (38.141878, -76.425198, 700),
     (38.144599, -76.428186, 100)],
    # Test 3 points with a consecutive duplicate
    [(38.142233, -76.434082, 300),
     (38.141878, -76.425198, 700),
     (38.141878, -76.425198, 700),
     (38.144599, -76.428186, 100)],
    # Test 4 points
    [(38.145574, -76.428492, 100),
     (38.149164, -76.427113, 750),
     (38.148662, -76.431517, 300),
     (38.146143, -76.426727, 500)],
    # Test 5 points
    [(38.145405, -76.428310, 100),
     (38.146582, -76.424099, 200),
     (38.144662, -76.427634, 300),
     (38.147729, -76.419185, 200),
     (38.147573, -76.420832, 100),
     (38.148522, -76.419507, 750)]
]

TESTDATA_MOVOBST_EVALCOLLISION = (
    # Obst radius and speed
    100, 200,
    # Positions (lat, lon, alt)
    [(38, -76, 100),
     (38.1, -76.1, 200)],
    # Time, Inside pos, outside pos
    [(0.0,
      [(38, -76, 100),
       (38, -76, 0),
       (38, -76, 200),
       (38.0001, -76, 100),
       (38, -76.0001, 100)],
      [(38.1, -76.1, 200),
       (38.1, -76.1, 100),
       (38.1, -76.1, 300),
       (38.002, -76.002, 100),
       (38, -76, 201),
       (38, -76, -1)]),
     (137.526986,
      [(38.1, -76.1, 200),
       (38.1, -76.1, 225),
       (38.1, -76.1, 175)],
      [(38, -76, 100),
       (38.1, -76.1, 350),
       (38.1, -76.1, 50)])
    ]
)

TESTDATA_FLYZONE_CONTAINSPOS = [
    # Check can't be inside polygon defined by 1 point
    {
        'min_alt': 0,
        'max_alt': 100,
        'waypoints': [
            (0, 0)
        ],
        'inside_pos': [],
        'outside_pos': [
            (0, 0, 0),
            (0, 0, 100),
            (100, 100, 0),
        ]
    },
    # Check can't be inside polygon defined by 2 points
    {
        'min_alt': 0,
        'max_alt':  100,
        'waypoints': [
            (0, 0),
            (100, 0),
        ],
        'inside_pos': [],
        'outside_pos': [
            (0, 0, 0),
            (0, 0, 100),
            (100, 0, 0),
            (100, 0, 100),
        ]
    },
    # Check polygon of 4 points
    {
        'min_alt': 0,
        'max_alt': 100,
        'waypoints': [
            (0, 0),
            (100, 0),
            (100, 100),
            (0, 100),
        ],
        'inside_pos': [
            (0.1, 0.1, 0),
            (0.1, 0.1, 100),
            (99.9, 0.1, 0),
            (99.9, 0.1, 100),
            (99.9, 99.9, 0),
            (99.9, 99.9, 100),
            (0.1, 99.9, 0),
            (0.1, 99.9, 100),
            (50, 50, 0),
            (50, 50, 50),
            (50, 50, 100),
        ],
        'outside_pos': [
            (0, 0, -1),
            (0, 0, 101),
            (50, 50, -1),
            (50, 50, 101),
            (100, 100, -1),
            (100, 100, 101),
            (-1, 0, 50),
            (0, -1, 50),
            (-1, -1, 50),
            (101, 0, 50),
            (0, 101, 50),
            (101, 101, 50),
        ]
    },
    # Check polygon of 3 points
    {
        'min_alt': 100,
        'max_alt': 750,
        'waypoints': [
            (0, 0),
            (100, 0),
            (50, 100),
        ],
        'inside_pos': [
            (0.1, 0.1, 100),
            (0.1, 0.1, 750),
            (99.9, 0.1, 100),
            (99.9, 0.1, 750),
            (50, 99.9, 100),
            (50, 99.9, 750),
            (25, 25, 100),
            (25, 25, 750),
            (1, 0.1, 100),
            (1, 0.1, 750),
            (99, 0.1, 100),
            (99, 0.1, 750),
            (50, 99, 100),
            (50, 99, 750),
        ],
        'outside_pos': [
            (25, 25, 99),
            (25, 25, 751),
            (-1, 0, 200),
            (0, -1, 200),
            (101, 0, 200),
            (51, 100, 200),
            (50, 101, 200),
        ]
    }
]

# ((alt_min, alt_max, [fly_zone_waypoints]),
#  [(uas_out_bounds_time, [uas_logs])])
TESTDATA_FLYZONE_EVALBOUNDS = (
    [(0, 100, [(38, -76), (39, -76), (39, -77), (38, -77)]),
     (100, 700, [(38, -76), (39, -76), (39, -77), (38, -77)])
    ],
    [(0.0,
      [(38.5, -76.5, 50, 0), (38.5, -76.5, 50, 1.0)]),
     (1.0,
      [(38.5, -76.5, 50, 0), (40, -76.5, 50, 1.0)]),
     (2.0,
      [(38.5, -76.5, 50, 0), (40, -76.5, 50, 1.0), (41, -76.5, 50, 2.0)]),
     (3.0,
      [(38.5, -76.5, 50, 0),
       (40, -76, 50, 1.0),
       (38.5, -76.5, 100, 2.0),
       (38.5, -76.5, 800, 3.0),
       (38.5, -76.5, 600, 4.0),
       (38.5, -78, 100, 5.0)])
     ]
)

# [satisfy_dist, waypoints, uas_logs, satisfied_list]
TESTDATA_MISSIONCONFIG_EVALWAYPOINTS = (
    100.0,
    [(38, -76, 100), (39, -77, 200), (37, -75, 0)],
    [(38, -76, 150), (40, -78, 600), (37, -75, 50), (38, 100, 0)],
    [True, False, True]
)

def clearTestDatabase():
    """Clears all objects from the test database."""
    classes = [
            AerialPosition,
            AccessLog,
            FlyZone,
            GpsPosition,
            MissionConfig,
            MovingObstacle,
            ObstacleAccessLog,
            ServerInfo,
            ServerInfoAccessLog,
            StationaryObstacle,
            TakeoffOrLandingEvent,
            UasTelemetry,
            Waypoint,
    ]
    for cur_class in classes:
        cur_class.objects.all().delete()
    cache.clear()


class TestHaversine(TestCase):
    """Tests the haversine code correctness."""

    def assertCloseEnough(self, distance_actual, distance_received,
                          threshold=0.003048):  # 10 feet in km
        """Determines whether the km distances given are close enough."""
        self.assertLessEqual(abs(distance_actual - distance_received),
                             threshold)

    def evaluate_inputs(self, input_output_list):
        """Evaluates a list of inputs and outputs."""
        for (lon1, lat1, lon2, lat2, distance_actual) in input_output_list:
            distance_received = haversine(lon1, lat1, lon2, lat2)
            self.assertCloseEnough(distance_actual, distance_received)

    def test_zero_distance(self):
        """Tests various latitudes and longitudes which have zero distance."""
        self.evaluate_inputs([
          # (lon1, lat1, lon2, lat2, dist_actual)
            (0,    0,    0,    0,    0),
            (1,    1,    1,    1,    0),
            (-1,   -1,   -1,   -1,   0),
            (1,    -1,   1,    -1,   0),
            (-1,   1,    -1,   1,    0),
            (76,   42,   76,   42,   0),
            (-76,  42,   -76,  42,   0),
        ])

    def test_hemisphere_distances(self):
        """Tests distances in each hemisphere."""
        self.evaluate_inputs([
          # (lon1, lat1, lon2, lat2, dist_actual)
            (-73,  40,   -74,  41,   139.6886345468666),
            (73,   40,   74,   41,   139.6886345468667),
            (73,   -40,  74,   -41,  139.6886345468667),
            (-73,  -40,  -74,  -41,  139.68863454686704),
        ])

    def test_competition_distances(self):
        """Tests distances representative of competition amounts."""
        self.evaluate_inputs([
          # (lon1,       lat1,      lon2,       lat2,      dist_actual)
            (-76.428709, 38.145306, -76.426375, 38.146146, 0.22446),
            (-76.428537, 38.145399, -76.427818, 38.144686, 0.10045),
            (-76.434261, 38.142471, -76.418876, 38.147838, 1.46914),
        ])


class TestKilometersToFeet(TestCase):
    """Tests the conversion from kilometers to feet."""

    def test_km_to_ft(self):
        """Performs a data-driven test of the conversion."""
        threshold = 5 # ft

        cases = [
          # (km,  ft_actual)
            (0,   0),
            (1,   3280.84),
            (1.5, 4921.26),
            (100, 328084),
        ]

        for (km, ft_actual) in cases:
            self.assertLess(abs(kilometersToFeet(km) - ft_actual), threshold)


class TestKnotsToFeetPerSecond(TestCase):
    """Tests the conversion from knots to feet per second."""

    def evaluate_conversion(self, knots, fps_actual):
        """Tests the conversion of the given input/output pair."""
        convert_thresh = 5
        return abs(knotsToFeetPerSecond(knots) - fps_actual) < convert_thresh

    def test_knots_to_fps(self):
        """Performs a data-drive test of the conversion."""
        threshold = 5 # ft/s

        cases = [
          # (knots, fps)
            (0.1,   0.168781),
            (1,     1.68781),
            (10,    16.8781),
            (100,   168.781),
        ]

        for (knots, fps_actual) in cases:
            self.assertLess(abs(knotsToFeetPerSecond(knots) - fps_actual), threshold)


class TestGpsPositionModel(TestCase):
    """Tests the GpsPosition model."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        pos = GpsPosition(latitude=10, longitude=100)
        pos.save()

        pos.__unicode__()

    def assertDistanceEqual(self, pos1, pos2, dist, threshold=10):
        """GpsPosition distances are within threshold (ft)."""
        self.assertAlmostEqual(pos1.distanceTo(pos2), dist, delta=threshold)
        self.assertAlmostEqual(pos2.distanceTo(pos1), dist, delta=threshold)

    def evaluate_inputs(self, io_list):
        """Evaluates the distanceTo calc with the given input list."""
        for (lon1, lat1, lon2, lat2, dist_actual) in io_list:
            gps1 = GpsPosition(latitude=lat1, longitude=lon1)
            gps1.save()

            gps2 = GpsPosition(latitude=lat2, longitude=lon2)
            gps2.save()

            self.assertDistanceEqual(gps1, gps2, dist_actual)

    def test_distance_zero(self):
        """Tests distance calc for same position."""
        self.evaluate_inputs([
          # (lon1, lat1, lon2, lat2, dist_actual)
            (0,    0,    0,    0,    0),
            (1,    1,    1,    1,    0),
            (-1,   -1,   -1,   -1,   0),
            (1,    -1,   1,    -1,   0),
            (-1,   1,    -1,   1,    0),
            (76,   42,   76,   42,   0),
            (-76,  42,   -76,  42,   0),
        ])

    def test_distance_competition_amounts(self):
        """Tests distance calc for competition amounts."""
        self.evaluate_inputs([
          # (lon1,       lat1,      lon2,       lat2,      dist_actual)
            (-76.428709, 38.145306, -76.426375, 38.146146, 736.4),
            (-76.428537, 38.145399, -76.427818, 38.144686, 329.6),
            (-76.434261, 38.142471, -76.418876, 38.147838, 4820.0),
        ])

class TestAerialPositionModel(TestCase):
    """Tests the AerialPosition model."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        gps = GpsPosition(latitude=10, longitude=100)
        gps.save()

        pos = AerialPosition(gps_position=gps, altitude_msl=100)
        pos.save()

        pos.__unicode__()

    def assertDistanceEqual(self, pos1, pos2, dist, threshold=10):
        """AerialPosition distances are within threshold (ft)."""
        self.assertAlmostEqual(pos1.distanceTo(pos2), dist, delta=threshold)
        self.assertAlmostEqual(pos2.distanceTo(pos1), dist, delta=threshold)

    def evaluate_inputs(self, io_list):
        """Evaluates the distanceTo calc with the given input list."""
        for (lon1, lat1, alt1, lon2, lat2, alt2, dist_actual) in io_list:
            gps1 = GpsPosition(latitude=lat1, longitude=lon1)
            gps1.save()

            gps2 = GpsPosition(latitude=lat2, longitude=lon2)
            gps2.save()

            pos1 = AerialPosition(gps_position=gps1, altitude_msl=alt1)
            pos2 = AerialPosition(gps_position=gps2, altitude_msl=alt2)

            self.assertDistanceEqual(pos1, pos2, dist_actual)

    def test_distance_zero(self):
        """Tests distance calc for same position."""
        self.evaluate_inputs([
          # (lon1, lat1, alt1, lon2, lat2, alt2, dist_actual)
            (0,    0,    0,    0,    0,    0,    0),
            (1,    2,    3,    1,    2,    3,    0),
            (-30,  30,   100,  -30,  30,   100,  0),
        ])

    def test_distance_competition_amounts(self):
        """Tests distance calc for competition amounts."""
        self.evaluate_inputs([
          # (lon1,       lat1,      alt1, lon2,       lat2,      alt2, dist_actual)
            (-76.428709, 38.145306, 0,    -76.426375, 38.146146, 0,    736.4),
            (-76.428537, 38.145399, 0,    -76.427818, 38.144686, 100,  344.4),
            (-76.434261, 38.142471, 100,  -76.418876, 38.147838, 800,  4873.7),
        ])


class TestWaypointModel(TestCase):
    """Tests the Waypoint model."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        gps = GpsPosition(latitude=10, longitude=100)
        gps.save()

        pos = AerialPosition(gps_position=gps, altitude_msl=100)
        pos.save()

        wpt = Waypoint(position=pos, order=10)
        wpt.save()

        wpt.__unicode__()

    def assertDistanceEqual(self, wpt1, wpt2, dist, threshold=10):
        """Waypoint distances are within threshold (ft)."""
        self.assertAlmostEqual(wpt1.distanceTo(wpt2), dist, delta=threshold)
        self.assertAlmostEqual(wpt2.distanceTo(wpt1), dist, delta=threshold)

    def evaluate_inputs(self, io_list):
        for (lon1, lat1, alt1, lon2, lat2, alt2, dist) in io_list:
            gps1 = GpsPosition(latitude=lat1, longitude=lon1)
            gps1.save()

            gps2 = GpsPosition(latitude=lat2, longitude=lon2)
            gps2.save()

            pos1 = AerialPosition(gps_position=gps1, altitude_msl=alt1)
            pos1.save()

            pos2 = AerialPosition(gps_position=gps2, altitude_msl=alt2)
            pos2.save()

            wpt1 = Waypoint(position=pos1)
            wpt2 = Waypoint(position=pos2)

            self.assertDistanceEqual(wpt1, wpt2, dist)

    def test_distance(self):
        """Tests the distance calculation executes correctly."""
        self.evaluate_inputs([
          # (lon1,       lat1,      alt1, lon2,       lat2,      alt2, dist_actual)
            (-76.428709, 38.145306, 0,    -76.426375, 38.146146, 0,    736.4),
            (-76.428537, 38.145399, 0,    -76.427818, 38.144686, 100,  344.4),
            (-76.434261, 38.142471, 100,  -76.418876, 38.147838, 800,  4873.7),
        ])


class TestServerInfoModel(TestCase):
    """Tests the ServerInfo model."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        info = ServerInfo(timestamp=timezone.now(),
                          team_msg='Test message.')
        info.save()

        info.__unicode__()

    def test_serialization(self):
        """Tests the JSON serialization method."""
        message = 'Hello, world.'
        time = timezone.now()

        server_info = ServerInfo(timestamp=time, team_msg=message)
        json_data = server_info.toJSON()

        self.assertTrue('message' in json_data)
        self.assertEqual(json_data['message'], message)
        self.assertTrue('message_timestamp' in json_data)
        self.assertEqual(json_data['message_timestamp'], str(time))


class TestAccessLogCommon(TestCase):
    """Common code for AccessLog model tests."""

    def setUp(self):
        """Sets up the tests."""
        self.user1 = User.objects.create_user('user1', 'email@example.com',
                                              'pass')

        self.user2 = User.objects.create_user('user2', 'email@example.com',
                                              'pass')

        self.year2000 = datetime.datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.year2001 = datetime.datetime(2001, 1, 1, tzinfo=timezone.utc)
        self.year2002 = datetime.datetime(2002, 1, 1, tzinfo=timezone.utc)
        self.year2003 = datetime.datetime(2003, 1, 1, tzinfo=timezone.utc)
        self.year2004 = datetime.datetime(2004, 1, 1, tzinfo=timezone.utc)

    def create_logs(self, user, num=10, start=None, delta=None):
        if start is None:
            start = timezone.now()
        if delta is None:
            delta = datetime.timedelta(seconds=1)

        logs = []

        for i in xrange(num):
            log = AccessLog(user=user)
            log.save()
            log.timestamp = start + i*delta # Wat.
            log.save()
            logs.append(log)

        return logs

class TestAccessLogBasic(TestAccessLogCommon):
    """Tests the AccessLog model basic functionality."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        log = AccessLog(timestamp=timezone.now(), user=self.user1)
        log.save()

        log.__unicode__()

    def test_no_data(self):
        self.assertEqual(0, len(AccessLog.getAccessLogForUser(self.user1)))

        self.assertEqual(0, len(AccessLog.getAccessLogForUserByTimePeriod([],
                                                                          [])))

        self.assertTupleEqual((None, None, None),
                              AccessLog.getAccessLogRates([], []))

    def test_basic_access(self):
        logs = self.create_logs(self.user1)

        results = AccessLog.getAccessLogForUser(self.user1)
        self.assertSequenceEqual(logs, results)

    def test_multi_user(self):
        # Intersperse logs from two users
        logs = []
        for _ in xrange(10):
            logs += self.create_logs(self.user1, num=1)
            self.create_logs(self.user2, num=1)

        results = AccessLog.getAccessLogForUser(self.user1)
        self.assertSequenceEqual(logs, results)

class TestAccessLogGetByPeriod(TestAccessLogCommon):
    """Test AccessLog.getAccessLogForUserByTimePeriod()"""

    def setUp(self):
        super(TestAccessLogGetByPeriod, self).setUp()

        self.year2000_logs = self.create_logs(self.user1, start=self.year2000)
        self.year2003_logs = self.create_logs(self.user1, start=self.year2003)
        self.logs = self.year2000_logs + self.year2003_logs

    def test_single_period(self):
        """Single set of logs accessible."""
        results = AccessLog.getAccessLogForUserByTimePeriod(self.logs, [
            (self.year2000, self.year2001),
        ])

        self.assertSequenceEqual([self.year2000_logs], results)

    def test_full_range(self):
        """All logs from (-inf, inf)."""
        results = AccessLog.getAccessLogForUserByTimePeriod(self.logs, [
            (None, None),
        ])

        self.assertSequenceEqual([self.logs], results)

    def test_both_periods(self):
        """Both sets of logs, accesses individually."""
        results = AccessLog.getAccessLogForUserByTimePeriod(self.logs, [
            (self.year2000, self.year2001),
            (self.year2003, self.year2004),
        ])

        self.assertSequenceEqual([self.year2000_logs, self.year2003_logs],
                                 results)

    def test_non_intersecting_period(self):
        """No logs matched."""
        results = AccessLog.getAccessLogForUserByTimePeriod(self.logs, [
            (self.year2001, self.year2002),
        ])

        self.assertSequenceEqual([[]], results)

    def test_one_intersecting_period(self):
        """Only one period matches logs."""
        results = AccessLog.getAccessLogForUserByTimePeriod(self.logs, [
            (self.year2001, self.year2002),
            (self.year2003, self.year2004),
        ])

        self.assertSequenceEqual([[], self.year2003_logs], results)

    def test_open_start(self):
        """Logs (-inf, 2001)"""
        results = AccessLog.getAccessLogForUserByTimePeriod(self.logs, [
            (None, self.year2001),
        ])

        self.assertSequenceEqual([self.year2000_logs], results)

    def test_open_end(self):
        """Logs (2003, inf)"""
        results = AccessLog.getAccessLogForUserByTimePeriod(self.logs, [
            (self.year2003, None),
        ])

        self.assertSequenceEqual([self.year2003_logs], results)

class TestAccessLogRates(TestAccessLogCommon):
    """Test AccessLog.getAccessLogRates()"""

    def consistent_period(self, logs, delta):
        # getAccessLogRates uses time between beginning/end of the period
        # and the first/last log to compute rates, so to get constant rates,
        # the period must begin and end delta seconds before/after the logs.
        return (logs[0].timestamp-delta, logs[-1].timestamp+delta)

    def test_constant_rate(self):
        """Rates computed correctly."""
        delta = datetime.timedelta(seconds=1)

        logs = self.create_logs(self.user1, delta=delta)
        period = self.consistent_period(logs, delta)

        rates = AccessLog.getAccessLogRates([period], [logs])

        self.assertSequenceEqual((1, 1, 1), rates)

    def test_ignore_start_end(self):
        """When start and end are None, only times between logs are compared."""
        delta = datetime.timedelta(seconds=1)

        logs = self.create_logs(self.user1, delta=delta)
        period = (None, None)

        rates = AccessLog.getAccessLogRates([period], [logs])

        self.assertSequenceEqual((1, 1, 1), rates)

    def test_multiple_periods(self):
        """Multiple periods are combined without introducing errors."""
        delta = datetime.timedelta(seconds=1)

        logs = [
            self.create_logs(self.user1, start=self.year2000, delta=delta),
            self.create_logs(self.user1, start=self.year2001, delta=delta),
        ]

        periods = [self.consistent_period(l, delta) for l in logs]

        rates = AccessLog.getAccessLogRates(periods, logs)

        self.assertSequenceEqual((1, 1, 1), rates)

    def test_different_deltas(self):
        """Sets of logs are combined for overall rates."""
        delta = datetime.timedelta(seconds=1)

        logs = [
            self.create_logs(self.user1, num=1000,
                             start=self.year2000, delta=delta),
            self.create_logs(self.user1, num=1000,
                             start=self.year2001, delta=delta/2),
        ]

        periods = [self.consistent_period(l, delta) for l in logs]

        rates = AccessLog.getAccessLogRates(periods, logs)

        self.assertAlmostEqual(0.5, rates[0]) # min
        self.assertAlmostEqual(1.0, rates[1]) # max
        self.assertAlmostEqual(0.75, rates[2], delta=0.001) # avg

class TestUasTelemetry(TestCase):
    """Tests the UasTelemetry model."""

    def tearDown(self):
        """Tears down the tests."""
        clearTestDatabase()

    def test_unicode(self):
        """Tests the unicode method executes."""
        pos = GpsPosition()
        pos.latitude = 100
        pos.longitude = 200
        pos.save()
        apos = AerialPosition()
        apos.gps_position = pos
        apos.altitude_msl = 200
        apos.save()
        log = UasTelemetry()
        log.timestamp = timezone.now()
        log.user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        log.uas_position = apos
        log.uas_heading = 100
        log.save()
        self.assertTrue(log.__unicode__())


class TestTakeoffOrLandingEventModel(TestCase):
    """Tests the TakeoffOrLandingEvent model."""

    def setUp(self):
        """Sets up the tests."""
        self.users = list()
        self.user_flight_periods = dict()
        self.base_time = timezone.now().replace(
                hour=0, minute=0, second=0, microsecond=0)
        for (username, logs, periods) in TESTDATA_TAKEOFFORLANDINGEVENT:
            # Create user
            user = User.objects.create_user(
                username, 'testemail@x.com', 'testpass')
            user.save()
            # Create log events
            for (time_offset, uas_in_air) in logs:
                event = TakeoffOrLandingEvent()
                event.user = user
                event.timestamp = self.base_time + datetime.timedelta(
                        seconds = time_offset)
                event.uas_in_air = uas_in_air
                event.save()
            # Create expected time periods
            user_periods = self.user_flight_periods.setdefault(user, list())
            for (time_start, time_end) in periods:
                if time_start is not None:
                    time_start = self.base_time + datetime.timedelta(
                            seconds = time_start)
                if time_end is not None:
                    time_end = self.base_time + datetime.timedelta(
                            seconds = time_end)
                user_periods.append((time_start, time_end))

    def tearDown(self):
        """Tears down the tests."""
        clearTestDatabase()

    def test_unicode(self):
        """Tests the unicode method executes."""
        log = TakeoffOrLandingEvent()
        log.timestamp = timezone.now()
        log.user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        log.uas_in_air = True
        log.save()
        self.assertTrue(log.__unicode__())

    def test_getFlightPeriodsForUser(self):
        """Tests the flight period list class method."""
        for user in self.users:
            flight_periods = TakeoffOrLandingEvent.getFlightPeriodsForUser(user)
            exp_periods = self.user_flight_periods[user]
            self.assertEqual(len(flight_periods), len(exp_periods))
            for period_id in range(len(flight_periods)):
                (period_start, period_end) = flight_periods[period_id]
                (exp_start, exp_end) = exp_periods[period_id]
                self.assertAlmostEqual(period_start, exp_start)
                self.assertAlmostEqual(period_end, exp_end)


class TestStationaryObstacleModel(TestCase):
    """Tests the StationaryObstacle model."""

    def tearDown(self):
        """Tears down the tests."""
        clearTestDatabase()

    def test_unicode(self):
        """Tests the unicode method executes."""
        pos = GpsPosition()
        pos.latitude = 100
        pos.longitude = 200
        pos.save()
        obst = StationaryObstacle()
        obst.gps_position = pos
        obst.cylinder_radius = 10
        obst.cylinder_height = 100
        obst.save()
        self.assertTrue(obst.__unicode__())

    def test_containsPos(self):
        """Tests the inside obstacle method."""
        # Form the test obstacle
        gps_position = GpsPosition()
        gps_position.latitude = TESTDATA_STATOBST_CONTAINSPOS_OBJ[0]
        gps_position.longitude = TESTDATA_STATOBST_CONTAINSPOS_OBJ[1]
        gps_position.save()
        obst = StationaryObstacle()
        obst.gps_position = gps_position
        obst.cylinder_radius = TESTDATA_STATOBST_CONTAINSPOS_OBJ[2]
        obst.cylinder_height = TESTDATA_STATOBST_CONTAINSPOS_OBJ[3]
        # Run test points against obstacle
        test_data = [
            (TESTDATA_STATOBST_CONTAINSPOS_INSIDE, True),
            (TESTDATA_STATOBST_CONTAINSPOS_OUTSIDE, False)
        ]
        for (cur_data, cur_contains) in test_data:
            for (lat, lon, alt) in cur_data:
                gps_position = GpsPosition()
                gps_position.latitude = lat
                gps_position.longitude = lon
                gps_position.save()
                aerial_pos = AerialPosition()
                aerial_pos.gps_position = gps_position
                aerial_pos.altitude_msl = alt
                self.assertEqual(obst.containsPos(aerial_pos), cur_contains)

    def test_evaluateCollisionWithUas(self):
        """Tests the collision with UAS method."""
        # Create testing data
        user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        user.save()
        (cyl_details, inside_pos, outside_pos) = TESTDATA_STATOBST_EVALCOLLISION
        (cyl_lat, cyl_lon, cyl_height, cyl_rad) = cyl_details
        gpos = GpsPosition()
        gpos.latitude = cyl_lat
        gpos.longitude = cyl_lon
        gpos.save()
        obst = StationaryObstacle()
        obst.gps_position = gpos
        obst.cylinder_radius = cyl_rad
        obst.cylinder_height = cyl_height
        obst.save()
        inside_logs = list()
        outside_logs = list()
        logs_to_create = [
                (inside_pos, inside_logs),
                (outside_pos, outside_logs)
        ]
        for (positions, log_list) in logs_to_create:
            for (lat, lon, alt) in positions:
                gpos = GpsPosition()
                gpos.latitude = lat
                gpos.longitude = lon
                gpos.save()
                apos = AerialPosition()
                apos.gps_position = gpos
                apos.altitude_msl = alt
                apos.save()
                log = UasTelemetry()
                log.user = user
                log.uas_position = apos
                log.uas_heading = 0
                log.save()
                log_list.append(log)
        # Assert collisions correctly evaluated
        collisions = [(inside_logs, True), (outside_logs, False)]
        for (log_list, inside) in collisions:
            self.assertEqual(
                    obst.evaluateCollisionWithUas(log_list),
                    inside)
            for log in log_list:
                self.assertEqual(
                        obst.evaluateCollisionWithUas([log]),
                        inside)

    def test_toJSON(self):
        """Tests the JSON serialization method."""
        TEST_LAT = 100.10
        TEST_LONG = 200.20
        TEST_RADIUS = 150.50
        TEST_HEIGHT = 75.30

        gps_position = GpsPosition()
        gps_position.latitude = TEST_LAT
        gps_position.longitude = TEST_LONG
        gps_position.save()
        obstacle = StationaryObstacle()
        obstacle.gps_position = gps_position
        obstacle.cylinder_radius = TEST_RADIUS
        obstacle.cylinder_height = TEST_HEIGHT
        json_data = obstacle.toJSON()

        self.assertTrue('latitude' in json_data)
        self.assertEqual(json_data['latitude'], TEST_LAT)
        self.assertTrue('longitude' in json_data)
        self.assertEqual(json_data['longitude'], TEST_LONG)
        self.assertTrue('cylinder_radius' in json_data)
        self.assertEqual(json_data['cylinder_radius'], TEST_RADIUS)
        self.assertTrue('cylinder_height' in json_data)
        self.assertEqual(json_data['cylinder_height'], TEST_HEIGHT)


class TestMovingObstacle(TestCase):
    """Tests the MovingObstacle model."""

    def setUp(self):
        """Create the obstacles for testing."""
        cache.clear()

        # Obstacle with no waypoints
        obst_no_wpt = MovingObstacle()
        obst_no_wpt.speed_avg = 1
        obst_no_wpt.sphere_radius = 1
        obst_no_wpt.save()
        self.obst_no_wpt = obst_no_wpt

        # Obstacle with single waypoint
        self.single_wpt_lat = 40
        self.single_wpt_lon = 76
        self.single_wpt_alt = 100
        obst_single_wpt = MovingObstacle()
        obst_single_wpt.speed_avg = 1
        obst_single_wpt.sphere_radius = 1
        obst_single_wpt.save()
        single_gpos = GpsPosition()
        single_gpos.latitude = self.single_wpt_lat
        single_gpos.longitude = self.single_wpt_lon
        single_gpos.save()
        single_apos = AerialPosition()
        single_apos.gps_position = single_gpos
        single_apos.altitude_msl = self.single_wpt_alt
        single_apos.save()
        single_wpt = Waypoint()
        single_wpt.position = single_apos
        single_wpt.name = 'Waypoint'
        single_wpt.order = 1
        single_wpt.save()
        obst_single_wpt.waypoints.add(single_wpt)
        self.obst_single_wpt = obst_single_wpt

        # Obstacles with predefined path
        self.obstacles = list()
        for path in TESTDATA_MOVOBST_PATHS:
            cur_obst = MovingObstacle()
            cur_obst.name = 'MovingObstacle'
            cur_obst.speed_avg = 68
            cur_obst.sphere_radius = 10
            cur_obst.save()
            for pt_id in range(len(path)):
                (lat, lon, alt) = path[pt_id]
                cur_gpos = GpsPosition()
                cur_gpos.latitude = lat
                cur_gpos.longitude = lon
                cur_gpos.save()
                cur_apos = AerialPosition()
                cur_apos.gps_position = cur_gpos
                cur_apos.altitude_msl = alt
                cur_apos.save()
                cur_wpt = Waypoint()
                cur_wpt.position = cur_apos
                cur_wpt.name = 'Waypoint'
                cur_wpt.order = pt_id
                cur_wpt.save()
                cur_obst.waypoints.add(cur_wpt)
            cur_obst.save()
            self.obstacles.append(cur_obst)

    def tearDown(self):
        """Tear down the obstacles created."""
        clearTestDatabase()

    def test_unicode(self):
        """Tests the unicode method executes."""
        obst = MovingObstacle()
        obst.speed_avg = 10
        obst.sphere_radius = 100
        obst.save()
        for _ in range(3):
          pos = GpsPosition()
          pos.latitude = 10
          pos.longitude = 100
          pos.save()
          apos = AerialPosition()
          apos.altitude_msl = 1000
          apos.gps_position = pos
          apos.save()
          wpt = Waypoint()
          wpt.position = apos
          wpt.order = 10
          wpt.save()
          obst.waypoints.add(wpt)
        self.assertTrue(obst.__unicode__())

    def test_getWaypointTravelTime_invalid_inputs(self):
        """Tests proper invalid input handling."""
        obstacle = MovingObstacle()
        obstacle.speed_avg = 1

        self.assertIsNone(obstacle.getWaypointTravelTime(None, 1, 1))
        self.assertIsNone(obstacle.getWaypointTravelTime([], 1, 1))
        self.assertIsNone(obstacle.getWaypointTravelTime([None], 1, 1))
        self.assertIsNone(obstacle.getWaypointTravelTime(
            [None, None], None, 1))
        self.assertIsNone(obstacle.getWaypointTravelTime(
            [None, None], 1, None))
        self.assertIsNone(obstacle.getWaypointTravelTime(
            [None, None], -1, 0))
        self.assertIsNone(obstacle.getWaypointTravelTime(
            [None, None], 0, -1))
        self.assertIsNone(obstacle.getWaypointTravelTime(
            [None, None], 2, 0))
        self.assertIsNone(obstacle.getWaypointTravelTime(
            [None, None], 0, 2))
        obstacle.speed_avg = 0
        self.assertIsNone(obstacle.getWaypointTravelTime(
            [None, None], 0, 1))

    def eval_travel_time(self, time_actual, time_received):
        """Evaluates whether the travel times are close enough."""
        EVAL_THRESH = time_actual * 0.1
        return abs(time_actual - time_received) < EVAL_THRESH

    def test_getWaypointTravelTime(self):
        """Tests travel time calc."""
        test_spds = [1, 10, 100, 500]
        for (lon2, lat2, lon1, lat1, dist_km) in TESTDATA_COMPETITION_DIST:
            dist_ft = kilometersToFeet(dist_km)
            for speed in test_spds:
                speed_fps = knotsToFeetPerSecond(speed)
                time = dist_ft / speed_fps
                gpos1 = GpsPosition()
                gpos1.latitude = lat1
                gpos1.longitude = lon1
                gpos1.save()
                apos1 = AerialPosition()
                apos1.gps_position = gpos1
                apos1.altitude_msl = 0
                apos1.save()
                wpt1 = Waypoint()
                wpt1.position = apos1
                gpos2 = GpsPosition()
                gpos2.latitude = lat2
                gpos2.longitude = lon2
                gpos2.save()
                apos2 = AerialPosition()
                apos2.gps_position = gpos2
                apos2.altitude_msl = 0
                apos2.save()
                wpt2 = Waypoint()
                wpt2.position = apos2
                waypoints = [wpt1, wpt2]
                obstacle = MovingObstacle()
                obstacle.speed_avg = speed
                self.assertTrue(self.eval_travel_time(
                    obstacle.getWaypointTravelTime(waypoints, 0, 1),
                    time))

    def test_getPosition_no_waypoints(self):
        """Tests position calc on no-waypoint."""
        self.assertEqual(self.obst_no_wpt.getPosition(), (0, 0, 0))

    def test_getPosition_one_waypoint(self):
        """Tests position calc on single waypoints."""
        (lat, lon, alt) = self.obst_single_wpt.getPosition()
        self.assertEqual(lat, self.single_wpt_lat)
        self.assertEqual(lon, self.single_wpt_lon)
        self.assertEqual(alt, self.single_wpt_alt)

    def test_getPosition_waypoints_plot(self):
        """Tests position calculation by saving plots of calculation.

        Saves plots to testOutput/auvsi_suas-MovingObstacle-getPosition-x.jpg.
        On each run it first deletes the existing folder. This requires manual
        inspection to validate correctness.
        """
        if not TEST_ENABLE_PLOTTING:
            return

        # Create directory for plot output
        if not os.path.exists('data'):
            os.mkdir('data')
        if os.path.exists('data/testOutput'):
            shutil.rmtree('data/testOutput')
        os.mkdir('data/testOutput')

        # Create plot for each path
        for obst_id in range(len(self.obstacles)):
            cur_obst = self.obstacles[obst_id]

            # Get waypoint positions as numpy array
            waypoints = cur_obst.waypoints.order_by('order')
            waypoint_travel_times = cur_obst.getInterWaypointTravelTimes(
                    waypoints)
            waypoint_times = cur_obst.getWaypointTimes(waypoint_travel_times)
            total_time = waypoint_times[len(waypoint_times)-1]
            num_waypoints = len(waypoints)
            wpt_latitudes = np.zeros(num_waypoints+1)
            wpt_longitudes = np.zeros(num_waypoints+1)
            wpt_altitudes = np.zeros(num_waypoints+1)
            for waypoint_id in range(num_waypoints+1):
                cur_id = waypoint_id % num_waypoints
                wpt_latitudes[waypoint_id] = (
                    waypoints[cur_id].position.gps_position.latitude)
                wpt_longitudes[waypoint_id] = (
                    waypoints[cur_id].position.gps_position.longitude)
                wpt_altitudes[waypoint_id] = (
                    waypoints[cur_id].position.altitude_msl)

            # Create time series to represent samples at 10 Hz for 1.5 trips
            time_pos = np.arange(0, 1.5*total_time, 0.10)
            # Sample position for the time series
            latitudes = np.zeros(len(time_pos))
            longitudes = np.zeros(len(time_pos))
            altitudes = np.zeros(len(time_pos))
            epoch = timezone.now().replace(
                year=1970, month=1, day=1, hour=0, minute=0, second=0,
                microsecond=0)
            for time_id in range(len(time_pos)):
                cur_time_offset = time_pos[time_id]
                cur_samp_time = (epoch +
                        datetime.timedelta(seconds=cur_time_offset))
                (lat, lon, alt) = cur_obst.getPosition(cur_samp_time)
                latitudes[time_id] = lat
                longitudes[time_id] = lon
                altitudes[time_id] = alt

            # Create plot
            plt.figure()
            plt.subplot(311)
            plt.plot(time_pos, latitudes, 'b',
                     waypoint_times, wpt_latitudes, 'rx')
            plt.subplot(312)
            plt.plot(time_pos, longitudes, 'b',
                     waypoint_times, wpt_longitudes, 'rx')
            plt.subplot(313)
            plt.plot(time_pos, altitudes, 'b',
                     waypoint_times, wpt_altitudes, 'rx')
            plt.savefig(('data/testOutput/auvsi_suas-MovingObstacle-getPosition-%d.jpg' %
                    obst_id))

    def test_containsPos(self):
        """Tests the inside obstacle method."""
        # Form the test obstacle
        obst = MovingObstacle()
        obst.sphere_radius = TESTDATA_MOVOBST_CONTAINSPOS_OBJ[2]
        # Run test points against obstacle
        test_data = [
            (TESTDATA_MOVOBST_CONTAINSPOS_INSIDE, True),
            (TESTDATA_MOVOBST_CONTAINSPOS_OUTSIDE, False)
        ]
        for (cur_data, cur_contains) in test_data:
            for (lat, lon, alt) in cur_data:
                gpos = GpsPosition()
                gpos.latitude = lat
                gpos.longitude = lon
                gpos.save()
                apos = AerialPosition()
                apos.gps_position = gpos
                apos.altitude_msl = alt
                self.assertEqual(
                        obst.containsPos(
                            TESTDATA_MOVOBST_CONTAINSPOS_OBJ[0],
                            TESTDATA_MOVOBST_CONTAINSPOS_OBJ[1],
                            TESTDATA_MOVOBST_CONTAINSPOS_OBJ[3],
                            apos),
                        cur_contains)

    def test_evaluateCollisionWithUas(self):
        """Tests the collision with UAS method."""
        # Get test data
        user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        user.save()
        testdata = TESTDATA_MOVOBST_EVALCOLLISION
        (obst_rad, obst_speed, obst_pos, log_details) = testdata
        # Create the obstacle
        obst = MovingObstacle()
        obst.speed_avg = obst_speed
        obst.sphere_radius = obst_rad
        obst.save()
        for pos_id in xrange(len(obst_pos)):
            (lat, lon, alt) = obst_pos[pos_id]
            gpos = GpsPosition()
            gpos.latitude = lat
            gpos.longitude = lon
            gpos.save()
            apos = AerialPosition()
            apos.gps_position = gpos
            apos.altitude_msl = alt
            apos.save()
            wpt = Waypoint()
            wpt.order = pos_id
            wpt.position = apos
            wpt.save()
            obst.waypoints.add(wpt)
        obst.save()
        # Create sets of logs
        epoch = timezone.now().replace(
                year=1970, month=1, day=1, hour=0, minute=0, second=0,
                microsecond=0)
        inside_logs = list()
        outside_logs = list()
        for (time_sec, inside_pos, outside_pos) in log_details:
            log_time = epoch + datetime.timedelta(seconds=time_sec)
            logs_pos = [(inside_pos, inside_logs), (outside_pos, outside_logs)]
            for (positions, log_list) in logs_pos:
                for (lat, lon, alt) in positions:
                    gpos = GpsPosition()
                    gpos.latitude = lat
                    gpos.longitude = lon
                    gpos.save()
                    apos = AerialPosition()
                    apos.gps_position = gpos
                    apos.altitude_msl = alt
                    apos.save()
                    log = UasTelemetry()
                    log.user = user
                    log.uas_position = apos
                    log.uas_heading = 0
                    log.save()
                    log.timestamp = log_time
                    log.save()
                    log_list.append(log)

        # Assert the obstacle correctly computes collisions
        log_collisions = [(True, inside_logs), (False, outside_logs)]
        for (inside, logs) in log_collisions:
            self.assertEqual(
                    obst.evaluateCollisionWithUas(logs),
                    inside)
            for log in logs:
                self.assertEqual(
                        obst.evaluateCollisionWithUas([log]),
                        inside)

    def test_toJSON(self):
        """Tests the JSON serialization method."""
        for cur_obst in self.obstacles:
            json_data = cur_obst.toJSON()
            self.assertTrue('latitude' in json_data)
            self.assertTrue('longitude' in json_data)
            self.assertTrue('altitude_msl' in json_data)
            self.assertTrue('sphere_radius' in json_data)
            self.assertEqual(json_data['sphere_radius'], cur_obst.sphere_radius)
        obst = self.obst_single_wpt
        json_data = obst.toJSON()
        self.assertEqual(json_data['latitude'],
                obst.waypoints.all()[0].position.gps_position.latitude)
        self.assertEqual(json_data['longitude'],
                obst.waypoints.all()[0].position.gps_position.longitude)
        self.assertEqual(json_data['altitude_msl'],
                obst.waypoints.all()[0].position.altitude_msl)


class TestFlyZone(TestCase):
    """Tests the FlyZone class."""

    def setUp(self):
        """Creates test data."""
        # Form test set for contains position
        self.testdata_containspos = list()
        for test_data in TESTDATA_FLYZONE_CONTAINSPOS:
            # Create the FlyZone
            fly_zone = FlyZone()
            fly_zone.altitude_msl_min = test_data['min_alt']
            fly_zone.altitude_msl_max = test_data['max_alt']
            fly_zone.save()
            for waypoint_id in range(len(test_data['waypoints'])):
                (lat, lon) = test_data['waypoints'][waypoint_id]
                gpos = GpsPosition()
                gpos.latitude = lat
                gpos.longitude = lon
                gpos.save()
                apos = AerialPosition()
                apos.gps_position = gpos
                apos.altitude_msl = 0
                apos.save()
                wpt = Waypoint()
                wpt.order = waypoint_id
                wpt.position = apos
                wpt.save()
                fly_zone.boundary_pts.add(wpt)
            # Form test set
            test_pos = list()
            for pos in test_data['inside_pos']:
                test_pos.append((pos, True))
            for pos in test_data['outside_pos']:
                test_pos.append((pos, False))
            # Store
            self.testdata_containspos.append((fly_zone, test_pos))
        
    def tearDown(self):
        """Destroys test data."""
        clearTestDatabase()

    def test_unicode(self):
        """Tests the unicode method executes."""
        zone = FlyZone()
        zone.altitude_msl_min = 1
        zone.altitude_msl_max = 2
        zone.save()
        for _ in range(3):
            pos = GpsPosition()
            pos.latitude = 10
            pos.longitude = 100
            pos.save()
            apos = AerialPosition()
            apos.altitude_msl = 1000
            apos.gps_position = pos
            apos.save()
            wpt = Waypoint()
            wpt.position = apos
            wpt.order = 10
            wpt.save()
            zone.boundary_pts.add(wpt)
        self.assertTrue(zone.__unicode__()) 

    def test_containsPos(self):
        """Tests the containsPos method."""
        for (fly_zone, test_pos) in self.testdata_containspos:        
            for ((lat, lon, alt), inside) in test_pos:
                gpos = GpsPosition()
                gpos.latitude = lat
                gpos.longitude = lon
                gpos.save()
                apos = AerialPosition()
                apos.altitude_msl = alt
                apos.gps_position = gpos
                self.assertEqual(fly_zone.containsPos(apos), inside)

    def test_containsManyPos(self):
        """Tests the containsManyPos method."""
        for (fly_zone, test_pos) in self.testdata_containspos:
            aerial_pos_list = list()
            expected_results = list()
            for ((lat, lon, alt), inside) in test_pos:
                gpos = GpsPosition()
                gpos.latitude = lat
                gpos.longitude = lon
                gpos.save()
                apos = AerialPosition()
                apos.altitude_msl = alt
                apos.gps_position = gpos
                aerial_pos_list.append(apos)
                expected_results.append(inside)
            self.assertEqual(
                    fly_zone.containsManyPos(aerial_pos_list), expected_results)

    def test_evaluateUasOutOfBounds(self):
        """Tests the UAS out of bounds method."""
        (fly_zone_details, uas_details) = TESTDATA_FLYZONE_EVALBOUNDS
        # Create FlyZone objects
        fly_zones = list()
        for (alt_min, alt_max, wpts) in fly_zone_details:
            zone = FlyZone()
            zone.altitude_msl_min = alt_min
            zone.altitude_msl_max = alt_max
            zone.save()
            for wpt_id in xrange(len(wpts)):
                (lat, lon) = wpts[wpt_id]
                gpos = GpsPosition()
                gpos.latitude = lat
                gpos.longitude = lon
                gpos.save()
                apos = AerialPosition()
                apos.gps_position = gpos
                apos.altitude_msl = 0
                apos.save()
                wpt = Waypoint()
                wpt.order = wpt_id
                wpt.position = apos
                wpt.save()
                zone.boundary_pts.add(wpt)
            zone.save()
            fly_zones.append(zone)

        # For each user, validate time out of bounds
        user_id = 0
        epoch = timezone.now().replace(
                year=1970, month=1, day=1, hour=0, minute=0, second=0,
                microsecond=0)
        for exp_out_of_bounds_time, uas_log_details in uas_details:
            # Create the logs
            user = User.objects.create_user(
                'testuser%d' % user_id, 'testemail@x.com', 'testpass')
            user_id += 1
            uas_logs = list()
            for (lat, lon, alt, timestamp) in uas_log_details:
                gpos = GpsPosition()
                gpos.latitude = lat
                gpos.longitude = lon
                gpos.save()
                apos = AerialPosition()
                apos.gps_position = gpos
                apos.altitude_msl = alt
                apos.save()
                log = UasTelemetry()
                log.user = user
                log.uas_position = apos
                log.uas_heading = 0
                log.save()
                log.timestamp = epoch + datetime.timedelta(
                        seconds=timestamp)
                log.save()
                uas_logs.append(log)
            # Assert out of bounds time matches expected
            out_of_bounds_time = FlyZone.evaluateUasOutOfBounds(
                    fly_zones, uas_logs)
            self.assertAlmostEqual(out_of_bounds_time, exp_out_of_bounds_time)


class TestMissionConfigModel(TestCase):
    """Tests the MissionConfig model."""

    def tearDown(self):
        """Destroys test data."""
        clearTestDatabase()

    def test_unicode(self):
        """Tests the unicode method executes."""
        pos = GpsPosition()
        pos.latitude = 10
        pos.longitude = 100
        pos.save()
        apos = AerialPosition()
        apos.altitude_msl = 1000
        apos.gps_position = pos
        apos.save()
        wpt = Waypoint()
        wpt.position = apos
        wpt.order = 10
        wpt.save()
        config = MissionConfig()
        config.mission_waypoints_dist_max = 1
        config.home_pos = pos
        config.emergent_last_known_pos = pos
        config.off_axis_target_pos = pos
        config.sric_pos = pos
        config.ir_target_pos = pos
        config.air_drop_pos = pos
        config.save()
        config.mission_waypoints.add(wpt)
        config.search_grid_points.add(wpt)
        config.emergent_grid_points.add(wpt)
        config.save()
        self.assertTrue(config.__unicode__())

    def test_evaluateUasSatisfiedWaypoints(self):
        """Tests the evaluation of waypoints method."""
        (satisfy_dist, waypoint_details, uas_log_details, exp_satisfied) = TESTDATA_MISSIONCONFIG_EVALWAYPOINTS
        # Create mission config
        gpos = GpsPosition()
        gpos.latitude = 10
        gpos.longitude = 10
        gpos.save()
        config = MissionConfig()
        config.home_pos = gpos
        config.mission_waypoints_dist_max = satisfy_dist
        config.emergent_last_known_pos = gpos
        config.off_axis_target_pos = gpos
        config.sric_pos = gpos
        config.ir_target_pos = gpos
        config.air_drop_pos = gpos
        config.save()
        # Create waypoints for config
        for wpt_id in xrange(len(waypoint_details)):
            (lat, lon, alt) = waypoint_details[wpt_id]
            pos = GpsPosition()
            pos.latitude = lat
            pos.longitude = lon
            pos.save()
            apos = AerialPosition()
            apos.altitude_msl = alt
            apos.gps_position = pos
            apos.save()
            wpt = Waypoint()
            wpt.position = apos
            wpt.order = wpt_id
            wpt.save()
            config.mission_waypoints.add(wpt)
        config.save()

        # Create UAS telemetry logs
        uas_logs = list()
        user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        for (lat, lon, alt) in uas_log_details:
            pos = GpsPosition()
            pos.latitude = lat
            pos.longitude = lon
            pos.save()
            apos = AerialPosition()
            apos.altitude_msl = alt
            apos.gps_position = pos
            apos.save()
            log = UasTelemetry()
            log.user = user
            log.uas_position = apos
            log.uas_heading = 0
            log.save()
            uas_logs.append(log)

        # Assert correct satisfied waypoints
        wpts_satisfied = config.evaluateUasSatisfiedWaypoints(uas_logs)
        self.assertEqual(wpts_satisfied, exp_satisfied)

class TestMissionConfigModelEvalTeams(TestCase):

    fixtures = ['testdata/sample_mission.json']

    def test_evaluateTeams(self):
        """Tests the evaluation of teams method."""
        user0 = User.objects.get(username='user0')
        user1 = User.objects.get(username='user1')
        config = MissionConfig.objects.get()

        teams = config.evaluateTeams()

        # Contains user0 and user1
        self.assertEqual(2, len(teams))

        # Verify dictionary structure
        for user, val in teams.iteritems():
            self.assertIn('waypoints_satisfied', val)
            self.assertIn(1, val['waypoints_satisfied'])
            self.assertIn(2, val['waypoints_satisfied'])

            self.assertIn('out_of_bounds_time', val)

            self.assertIn('interop_times', val)

            for key in ['server_info', 'obst_info', 'uas_telem']:
                self.assertIn(key, val['interop_times'])
                self.assertIn('min', val['interop_times'][key])
                self.assertIn('max', val['interop_times'][key])
                self.assertIn('avg', val['interop_times'][key])

            self.assertIn('stationary_obst_collision', val)
            self.assertIn(25, val['stationary_obst_collision'])
            self.assertIn(26, val['stationary_obst_collision'])

            self.assertIn('moving_obst_collision', val)
            self.assertIn(25, val['moving_obst_collision'])
            self.assertIn(26, val['moving_obst_collision'])

        # user0 data
        self.assertEqual(True, teams[user0]['waypoints_satisfied'][1])
        self.assertEqual(False, teams[user0]['waypoints_satisfied'][2])

        self.assertAlmostEqual(0.6, teams[user0]['out_of_bounds_time'])

        self.assertAlmostEqual(0.0, teams[user0]['interop_times']['server_info']['min'])
        self.assertAlmostEqual(0.4, teams[user0]['interop_times']['server_info']['max'])
        self.assertAlmostEqual(1./6, teams[user0]['interop_times']['server_info']['avg'])

        self.assertAlmostEqual(0.0, teams[user0]['interop_times']['obst_info']['min'])
        self.assertAlmostEqual(0.5, teams[user0]['interop_times']['obst_info']['max'])
        self.assertAlmostEqual(1./5, teams[user0]['interop_times']['obst_info']['avg'])

        self.assertAlmostEqual(0.0, teams[user0]['interop_times']['uas_telem']['min'])
        self.assertAlmostEqual(0.5, teams[user0]['interop_times']['uas_telem']['max'])
        self.assertAlmostEqual(1./6, teams[user0]['interop_times']['uas_telem']['avg'])

        self.assertEqual(True, teams[user0]['stationary_obst_collision'][25])
        self.assertEqual(False, teams[user0]['stationary_obst_collision'][26])

        self.assertEqual(True, teams[user0]['moving_obst_collision'][25])
        self.assertEqual(False, teams[user0]['moving_obst_collision'][26])

        # user1 data
        self.assertEqual(True, teams[user1]['waypoints_satisfied'][1])
        self.assertEqual(True, teams[user1]['waypoints_satisfied'][2])

        self.assertAlmostEqual(1.0, teams[user1]['out_of_bounds_time'])

        self.assertAlmostEqual(0.1, teams[user1]['interop_times']['server_info']['min'])
        self.assertAlmostEqual(0.5, teams[user1]['interop_times']['server_info']['max'])
        self.assertAlmostEqual(1./3, teams[user1]['interop_times']['server_info']['avg'])

        self.assertAlmostEqual(0.1, teams[user1]['interop_times']['obst_info']['min'])
        self.assertAlmostEqual(0.4, teams[user1]['interop_times']['obst_info']['max'])
        self.assertAlmostEqual(1./4, teams[user1]['interop_times']['obst_info']['avg'])

        self.assertAlmostEqual(0.0, teams[user1]['interop_times']['uas_telem']['min'])
        self.assertAlmostEqual(1.0, teams[user1]['interop_times']['uas_telem']['max'])
        self.assertAlmostEqual(1./3, teams[user1]['interop_times']['uas_telem']['avg'])

        self.assertEqual(False, teams[user1]['stationary_obst_collision'][25])
        self.assertEqual(False, teams[user1]['stationary_obst_collision'][26])

        self.assertEqual(False, teams[user1]['moving_obst_collision'][25])
        self.assertEqual(False, teams[user1]['moving_obst_collision'][26])

class TestLoginUserView(TestCase):
    """Tests the loginUser view."""

    def setUp(self):
        """Sets up the test by creating a test user."""
        self.user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        self.user.save()
        self.client = Client()
        self.loginUrl = reverse('auvsi_suas:login')

    def tearDown(self):
        """Deletes users for the view."""
        clearTestDatabase()

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        client = self.client
        loginUrl = self.loginUrl

        # Test GET instead of POST
        response = client.get(loginUrl)
        self.assertEqual(response.status_code, 400)

        # Test POST with no parameters
        response = client.post(loginUrl)
        self.assertEqual(response.status_code, 400)

        # Test POST with a missing parameter
        response = client.post(loginUrl, {'username': 'test'})
        self.assertEqual(response.status_code, 400)
        response = client.post(loginUrl, {'password': 'test'})
        self.assertEqual(response.status_code, 400)


    def test_invalid_credentials(self):
        """Tests invalid credentials for login."""
        client = self.client
        loginUrl = self.loginUrl
        response = client.post(loginUrl, {'username': 'a', 'password': 'b'})
        self.assertEqual(response.status_code, 400)

    def test_correct_credentials(self):
        """Tests correct credentials for login."""
        client = self.client
        loginUrl = self.loginUrl
        response = client.post(
                loginUrl, {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 200)


class TestGetServerInfoView(TestCase):
    """Tests the getServerInfo view."""

    def setUp(self):
        """Sets up the client, server info URL, and user."""
        self.user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        self.user.save()
        self.info = ServerInfo()
        self.info.team_msg = 'test message'
        self.info.save()
        self.client = Client()
        self.loginUrl = reverse('auvsi_suas:login')
        self.infoUrl = reverse('auvsi_suas:server_info')
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Destroys the user."""
        clearTestDatabase()

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        client = self.client
        infoUrl = self.infoUrl

        response = client.get(infoUrl)
        self.assertEqual(response.status_code, 400)

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        client = self.client
        loginUrl = self.loginUrl
        infoUrl = self.infoUrl

        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        response = client.post(infoUrl)
        self.assertEqual(response.status_code, 400)

    def test_correct_log_and_response(self):
        """Tests that access is logged and returns valid response."""
        client = self.client
        loginUrl = self.loginUrl
        infoUrl = self.infoUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        response = client.get(infoUrl)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ServerInfoAccessLog.objects.all()), 1)
        access_log = ServerInfoAccessLog.objects.all()[0]
        self.assertEqual(access_log.user, self.user)
        json_data = json.loads(response.content)
        self.assertTrue('server_info' in json_data)
        self.assertTrue('server_time' in json_data)

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        if not TEST_ENABLE_LOADTEST:
            return

        client = self.client
        loginUrl = self.loginUrl
        infoUrl = self.infoUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        total_ops = 0
        start_t = time.clock()
        while time.clock() - start_t < OP_RATE_T:
            client.get(infoUrl)
            total_ops += 1
        end_t = time.clock()
        total_t = end_t - start_t
        op_rate = total_ops / total_t

        print 'Server Info Rate (%f)' % op_rate
        self.assertGreaterEqual(op_rate, OP_RATE_INDIV_THRESH)


class TestGetObstaclesView(TestCase):
    """Tests the getObstacles view."""

    def setUp(self):
        """Sets up the client, obstacle URL, obstacles, and user."""
        # Setup user
        self.user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        self.user.save()
        # Setup the obstacles
        for path in TESTDATA_MOVOBST_PATHS:
            # Stationary obstacle
            (stat_lat, stat_lon, _) = path[0]
            stat_gps = GpsPosition()
            stat_gps.latitude = stat_lat
            stat_gps.longitude = stat_lon
            stat_gps.save()
            stat_obst = StationaryObstacle()
            stat_obst.gps_position = stat_gps
            stat_obst.cylinder_radius = 100
            stat_obst.cylinder_height = 200
            stat_obst.save()
            # Moving obstacle
            mov_obst = MovingObstacle()
            mov_obst.speed_avg = 40
            mov_obst.sphere_radius = 100
            mov_obst.save()
            for pt_id  in range(len(path)):
                # Obstacle waypoints
                (wpt_lat, wpt_lon, wpt_alt) = path[pt_id]
                gpos = GpsPosition()
                gpos.latitude = wpt_lat
                gpos.longitude = wpt_lon
                gpos.save()
                apos = AerialPosition()
                apos.altitude_msl = wpt_alt
                apos.gps_position = gpos
                apos.save()
                wpt = Waypoint()
                wpt.name = 'test waypoint'
                wpt.order = pt_id
                wpt.position = apos
                wpt.save()
                mov_obst.waypoints.add(wpt)
            mov_obst.save()
        # Setup test objs
        self.client = Client()
        self.loginUrl = reverse('auvsi_suas:login')
        self.obstUrl = reverse('auvsi_suas:obstacles')
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Destroys the user."""
        clearTestDatabase()

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        client = self.client
        obstUrl = self.obstUrl
        response = client.get(obstUrl)
        self.assertEqual(response.status_code, 400)

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        client = self.client
        loginUrl = self.loginUrl
        obstUrl = self.obstUrl

        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        response = client.post(obstUrl)
        self.assertEqual(response.status_code, 400)

    def test_correct_log_and_response(self):
        """Tests that access is logged and returns valid response."""
        client = self.client
        loginUrl = self.loginUrl
        obstUrl = self.obstUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        response = client.get(obstUrl)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue('stationary_obstacles' in json_data)
        self.assertTrue('moving_obstacles' in json_data)
        self.assertEqual(len(ObstacleAccessLog.objects.all()), 1)

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        if not TEST_ENABLE_LOADTEST:
            return

        client = self.client
        loginUrl = self.loginUrl
        obstUrl = self.obstUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        total_ops = 0
        start_t = time.clock()
        while time.clock() - start_t < OP_RATE_T:
            client.get(obstUrl)
            total_ops += 1
        end_t = time.clock()
        total_t = end_t - start_t
        op_rate = total_ops / total_t

        print 'Obstacle Info Rate (%f)' % op_rate
        self.assertGreaterEqual(op_rate, OP_RATE_INDIV_THRESH)


class TestPostUasPosition(TestCase):
    """Tests the postUasPosition view."""

    def setUp(self):
        """Sets up the client, server info URL, and user."""
        self.user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        self.user.save()
        self.client = Client()
        self.loginUrl = reverse('auvsi_suas:login')
        self.uasUrl = reverse('auvsi_suas:uas_telemetry')
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Destroys the user."""
        clearTestDatabase()

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        client = self.client
        uasUrl = self.uasUrl
        response = client.get(uasUrl)
        self.assertEqual(response.status_code, 400)

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        client = self.client
        loginUrl = self.loginUrl
        uasUrl = self.uasUrl

        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        response = client.post(uasUrl)
        self.assertEqual(response.status_code, 400)
        response = client.post(uasUrl,
                {'longitude': 0,
                 'altitude_msl': 0,
                 'uas_heading': 0})
        self.assertEqual(response.status_code, 400)
        response = client.post(uasUrl,
                {'latitude': 0,
                 'altitude_msl': 0,
                 'uas_heading': 0})
        self.assertEqual(response.status_code, 400)
        response = client.post(uasUrl,
                {'latitude': 0,
                 'longitude': 0,
                 'uas_heading': 0})
        self.assertEqual(response.status_code, 400)
        response = client.post(uasUrl,
                {'latitude': 0,
                 'longitude': 0,
                 'altitude_msl': 0})
        self.assertEqual(response.status_code, 400)

    def eval_request_values(self, lat, lon, alt, heading):
        client = self.client
        uasUrl = self.uasUrl
        response = client.post(uasUrl,
                {'latitude': lat,
                 'longitude': lon,
                 'altitude_msl': alt,
                 'uas_heading': heading})
        return response.status_code

    def test_invalid_request_values(self):
        """Tests by specifying correct parameters with invalid values."""
        client = self.client
        loginUrl = self.loginUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        TEST_DATA = [
            (-100, 0, 0, 0),
            (100, 0, 0, 0),
            (0, -190, 0, 0),
            (0, 190, 0, 0),
            (0, 0, 0, -10),
            (0, 0, 0, 370)]
        for (lat, lon, alt, heading) in TEST_DATA:
            self.assertEqual(400,
                self.eval_request_values(lat, lon, alt, heading))

    def test_upload_and_store(self):
        """Tests correct upload and storage of data."""
        client = self.client
        loginUrl = self.loginUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        uasUrl = self.uasUrl

        lat = 10
        lon = 20
        alt = 30
        heading = 40
        response = client.post(uasUrl,
                {'latitude': lat,
                 'longitude': lon,
                 'altitude_msl': alt,
                 'uas_heading': heading})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(UasTelemetry.objects.all()), 1)
        obj = UasTelemetry.objects.all()[0]
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.uas_heading, heading)
        self.assertEqual(obj.uas_position.altitude_msl, alt)
        self.assertEqual(obj.uas_position.gps_position.latitude, lat)
        self.assertEqual(obj.uas_position.gps_position.longitude, lon)

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        if not TEST_ENABLE_LOADTEST:
            return

        client = self.client
        loginUrl = self.loginUrl
        uasUrl = self.uasUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        lat = 10
        lon = 20
        alt = 30
        heading = 40
        total_ops = 0
        start_t = time.clock()
        while time.clock() - start_t < OP_RATE_T:
            client.post(uasUrl,
                    {'latitude': lat,
                     'longiutde': lon,
                     'altitude_msl': alt,
                     'uas_heading': heading})
            total_ops += 1
        end_t = time.clock()
        total_t = end_t - start_t
        op_rate = total_ops / total_t

        print 'UAS Post Rate (%f)' % op_rate
        self.assertGreaterEqual(op_rate, OP_RATE_INDIV_THRESH)


class TestEvaluateTeams(TestCase):
    """Tests the evaluateTeams view."""

    fixtures = ['testdata/sample_mission.json']

    def setUp(self):
        """Sets up the tests."""
        # Create nonadmin user
        self.nonadmin_user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        self.nonadmin_user.save()
        self.nonadmin_client = Client()
        # Create admin user
        self.admin_user = User.objects.create_superuser(
                'testuser2', 'testemail@x.com', 'testpass')
        self.admin_user.save()
        self.admin_client = Client()
        # Create URLs for testing
        self.loginUrl = reverse('auvsi_suas:login')
        self.evalUrl = reverse('auvsi_suas:evaluate_teams')
        logging.disable(logging.CRITICAL)

    def test_evaluateTeams_nonadmin(self):
        """Tests that you can only access data as admin."""
        client = self.client
        loginUrl = self.loginUrl
        evalUrl = self.evalUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        response = client.get(evalUrl)
        self.assertGreaterEqual(response.status_code, 300)

    def test_evaluateTeams(self):
        """Tests the CSV method."""
        client = self.client
        loginUrl = self.loginUrl
        evalUrl = self.evalUrl
        client.post(loginUrl, {'username': 'testuser2', 'password': 'testpass'})
        response = client.get(evalUrl)
        self.assertEqual(response.status_code, 200)
        csv_data = response.content
        # Check correct number of rows
        self.assertEqual(len(csv_data.split('\n')), 5)
        # Check some headers
        self.assertTrue('username' in csv_data)
        self.assertTrue('interop_times.server_info.min' in csv_data)
        # Check username fields
        self.assertTrue('user0' in csv_data)
        self.assertTrue('user1' in csv_data)

