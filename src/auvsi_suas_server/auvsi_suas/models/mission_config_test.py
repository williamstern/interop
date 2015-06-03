"""Tests for the mission_config module."""

from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import Waypoint
from django.contrib.auth.models import User
from django.test import TestCase


# [satisfy_dist, waypoints, uas_logs, satisfied_list]
TESTDATA_MISSIONCONFIG_EVALWAYPOINTS = (
    100.0,
    [(38, -76, 100), (39, -77, 200), (37, -75, 0)],
    [(38, -76, 150), (40, -78, 600), (37, -75, 50), (38, 100, 0)],
    [True, False, True]
)


class TestMissionConfigModel(TestCase):
    """Tests the MissionConfig model."""

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
        config.ir_primary_target_pos = pos
        config.ir_secondary_target_pos = pos
        config.air_drop_pos = pos
        config.save()
        config.mission_waypoints.add(wpt)
        config.search_grid_points.add(wpt)
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
        config.ir_primary_target_pos = gpos
        config.ir_secondary_target_pos = gpos
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
