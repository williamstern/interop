"""Tests for the mission_config module."""

import datetime
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.fly_zone import FlyZone
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.mission_config import MissionConfig
from auvsi_suas.models.uas_telemetry import UasTelemetry
from auvsi_suas.models.waypoint import Waypoint
from auvsi_suas.patches.simplekml_patch import Kml
from auvsi_suas.proto.mission_pb2 import WaypointEvaluation
from django.contrib.auth.models import User
from django.test import TestCase


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
        config.home_pos = pos
        config.emergent_last_known_pos = pos
        config.off_axis_target_pos = pos
        config.air_drop_pos = pos
        config.save()
        config.mission_waypoints.add(wpt)
        config.search_grid_points.add(wpt)
        config.save()
        self.assertTrue(config.__unicode__())

    def create_uas_logs(self, user, entries):
        """Create a list of uas telemetry logs.

        Args:
            user: User to create logs for.
            entries: List of (lat, lon, alt) tuples for each entry.

        Returns:
            List of UasTelemetry objects
        """
        ret = []

        for (lat, lon, alt) in entries:
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
            ret.append(log)

        return ret

    def assertSatisfiedWaypoints(self, expect, got):
        """Assert two satisfied_waypoints return values are equal."""
        self.assertEqual(len(expect), len(got))
        for i in xrange(len(expect)):
            e = expect[i]
            g = got[i]
            self.assertEqual(e.id, g.id)
            self.assertAlmostEqual(e.score_ratio, g.score_ratio, places=2)
            self.assertAlmostEqual(e.closest_for_scored_approach_ft,
                                   g.closest_for_scored_approach_ft,
                                   places=2)
            self.assertAlmostEqual(e.closest_for_mission_ft,
                                   g.closest_for_mission_ft,
                                   places=2)

    def test_satisfied_waypoints(self):
        """Tests the evaluation of waypoints method."""
        # Create mission config
        gpos = GpsPosition()
        gpos.latitude = 10
        gpos.longitude = 10
        gpos.save()
        config = MissionConfig()
        config.home_pos = gpos
        config.emergent_last_known_pos = gpos
        config.off_axis_target_pos = gpos
        config.air_drop_pos = gpos
        config.save()

        # Create waypoints for config
        waypoints = [(38, -76, 100), (39, -77, 200), (40, -78, 0)]
        for i, waypoint in enumerate(waypoints):
            (lat, lon, alt) = waypoint
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
            wpt.order = i
            wpt.save()
            config.mission_waypoints.add(wpt)
        config.save()

        # Create UAS telemetry logs
        user = User.objects.create_user('testuser', 'testemail@x.com',
                                        'testpass')

        # Only first is valid.
        entries = [(38, -76, 140), (40, -78, 600), (37, -75, 40)]
        logs = self.create_uas_logs(user, entries)
        expect = [WaypointEvaluation(id=0,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40),
                  WaypointEvaluation(id=1,
                                     score_ratio=0,
                                     closest_for_mission_ft=460785.17),
                  WaypointEvaluation(id=2,
                                     score_ratio=0)]
        self.assertSatisfiedWaypoints(expect, config.satisfied_waypoints(logs))

        # First and last are valid, but missed second, so third doesn't count.
        entries = [(38, -76, 140), (40, -78, 600), (40, -78, 40)]
        logs = self.create_uas_logs(user, entries)
        expect = [WaypointEvaluation(id=0,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40),
                  WaypointEvaluation(id=1,
                                     score_ratio=0,
                                     closest_for_mission_ft=460785.03),
                  WaypointEvaluation(id=2,
                                     score_ratio=0)]
        self.assertSatisfiedWaypoints(expect, config.satisfied_waypoints(logs))

        # Hit all.
        entries = [(38, -76, 140), (39, -77, 180), (40, -78, 40)]
        expect = [WaypointEvaluation(id=0,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40),
                  WaypointEvaluation(id=1,
                                     score_ratio=0.8,
                                     closest_for_scored_approach_ft=20,
                                     closest_for_mission_ft=20),
                  WaypointEvaluation(id=2,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40)]
        logs = self.create_uas_logs(user, entries)
        self.assertSatisfiedWaypoints(expect, config.satisfied_waypoints(logs))

        # Only hit the first waypoint on run one, hit all on run two.
        entries = [(38, -76, 140),
                   (40, -78, 600),
                   (37, -75, 40),
                   # Run two:
                   (38, -76, 140),
                   (39, -77, 180),
                   (40, -78, 40)]
        logs = self.create_uas_logs(user, entries)
        expect = [WaypointEvaluation(id=0,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40),
                  WaypointEvaluation(id=1,
                                     score_ratio=0.8,
                                     closest_for_scored_approach_ft=20,
                                     closest_for_mission_ft=20),
                  WaypointEvaluation(id=2,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40)]
        self.assertSatisfiedWaypoints(expect, config.satisfied_waypoints(logs))

        # Hit all on run one, only hit the first waypoint on run two.
        entries = [(38, -76, 140),
                   (39, -77, 180),
                   (40, -78, 40),
                   # Run two:
                   (38, -76, 140),
                   (40, -78, 600),
                   (37, -75, 40)]
        expect = [WaypointEvaluation(id=0,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40),
                  WaypointEvaluation(id=1,
                                     score_ratio=0.8,
                                     closest_for_scored_approach_ft=20,
                                     closest_for_mission_ft=20),
                  WaypointEvaluation(id=2,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40)]
        logs = self.create_uas_logs(user, entries)
        self.assertSatisfiedWaypoints(expect, config.satisfied_waypoints(logs))

        # Keep flying after hitting all waypoints.
        entries = [(38, -76, 140), (39, -77, 180), (40, -78, 40),
                   (30.1, -78.1, 100)]
        logs = self.create_uas_logs(user, entries)
        expect = [WaypointEvaluation(id=0,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40),
                  WaypointEvaluation(id=1,
                                     score_ratio=0.8,
                                     closest_for_scored_approach_ft=20,
                                     closest_for_mission_ft=20),
                  WaypointEvaluation(id=2,
                                     score_ratio=0.6,
                                     closest_for_scored_approach_ft=40,
                                     closest_for_mission_ft=40)]
        self.assertSatisfiedWaypoints(expect, config.satisfied_waypoints(logs))

        # Hit all in first run, but second is higher scoring.
        entries = [(38, -76, 140),
                   (39, -77, 180),
                   (40, -78, 60),
                   # Run two:
                   (38, -76, 100),
                   (39, -77, 200),
                   (40, -78, 110)]
        logs = self.create_uas_logs(user, entries)
        expect = [WaypointEvaluation(id=0,
                                     score_ratio=1,
                                     closest_for_scored_approach_ft=0,
                                     closest_for_mission_ft=0),
                  WaypointEvaluation(id=1,
                                     score_ratio=1,
                                     closest_for_scored_approach_ft=0,
                                     closest_for_mission_ft=0),
                  WaypointEvaluation(id=2,
                                     score_ratio=0,
                                     closest_for_mission_ft=60)]
        self.assertSatisfiedWaypoints(expect, config.satisfied_waypoints(logs))

        # Restart waypoint path in the middle.
        waypoints = [(38, -76, 100), (39, -77, 200), (40, -78, 0)]
        entries = [(38, -76, 140),
                   (39, -77, 180),
                   # Restart:
                   (38, -76, 70),
                   (39, -77, 150),
                   (40, -78, 10)]
        logs = self.create_uas_logs(user, entries)
        expect = [WaypointEvaluation(id=0,
                                     score_ratio=0.7,
                                     closest_for_scored_approach_ft=30,
                                     closest_for_mission_ft=30),
                  WaypointEvaluation(id=1,
                                     score_ratio=0.5,
                                     closest_for_scored_approach_ft=50,
                                     closest_for_mission_ft=20),
                  WaypointEvaluation(id=2,
                                     score_ratio=0.9,
                                     closest_for_scored_approach_ft=10,
                                     closest_for_mission_ft=10)]
        self.assertSatisfiedWaypoints(expect, config.satisfied_waypoints(logs))


class TestMissionConfigModelSampleMission(TestCase):

    fixtures = ['testdata/sample_mission.json']

    def test_evaluate_teams(self):
        """Tests the evaluation of teams method."""
        user0 = User.objects.get(username='user0')
        user1 = User.objects.get(username='user1')
        config = MissionConfig.objects.get()

        mission_eval = config.evaluate_teams()

        # Contains user0 and user1
        self.assertEqual(2, len(mission_eval.teams))

        # user0 data
        user_eval = mission_eval.teams[0]
        self.assertEqual(user0.username, user_eval.team)
        feedback = user_eval.feedback
        self.assertEqual(0.0,
                         feedback.waypoints[0].closest_for_scored_approach_ft)
        self.assertEqual(1.0, feedback.waypoints[0].score_ratio)
        self.assertEqual(0.0,
                         feedback.waypoints[1].closest_for_scored_approach_ft)
        self.assertAlmostEqual(2, feedback.mission_clock_time_sec)
        self.assertAlmostEqual(0.6, feedback.out_of_bounds_time_sec)

        self.assertAlmostEqual(0.5, feedback.uas_telemetry_time_max_sec)
        self.assertAlmostEqual(1. / 6, feedback.uas_telemetry_time_avg_sec)

        self.assertAlmostEqual(0.445, feedback.target.score_ratio, places=3)

        self.assertEqual(25, feedback.stationary_obstacles[0].id)
        self.assertEqual(True, feedback.stationary_obstacles[0].hit)
        self.assertEqual(26, feedback.stationary_obstacles[1].id)
        self.assertEqual(False, feedback.stationary_obstacles[1].hit)

        self.assertEqual(25, feedback.moving_obstacles[0].id)
        self.assertEqual(True, feedback.moving_obstacles[0].hit)
        self.assertEqual(26, feedback.moving_obstacles[1].id)
        self.assertEqual(False, feedback.moving_obstacles[1].hit)

        # user1 data
        user_eval = mission_eval.teams[1]
        self.assertEqual(user1.username, user_eval.team)
        feedback = user_eval.feedback
        self.assertEqual(0.0,
                         feedback.waypoints[0].closest_for_scored_approach_ft)
        self.assertEqual(1.0, feedback.waypoints[0].score_ratio)
        self.assertEqual(0.0,
                         feedback.waypoints[1].closest_for_scored_approach_ft)
        self.assertAlmostEqual(18, feedback.mission_clock_time_sec)
        self.assertAlmostEqual(1.0, feedback.out_of_bounds_time_sec)

        self.assertAlmostEqual(2.0, feedback.uas_telemetry_time_max_sec)
        self.assertAlmostEqual(1.0, feedback.uas_telemetry_time_avg_sec)

        self.assertAlmostEqual(0, feedback.target.score_ratio, places=3)

        self.assertEqual(25, feedback.stationary_obstacles[0].id)
        self.assertEqual(False, feedback.stationary_obstacles[0].hit)
        self.assertEqual(26, feedback.stationary_obstacles[1].id)
        self.assertEqual(False, feedback.stationary_obstacles[1].hit)

        self.assertEqual(25, feedback.moving_obstacles[0].id)
        self.assertEqual(False, feedback.moving_obstacles[0].hit)
        self.assertEqual(26, feedback.moving_obstacles[1].id)
        self.assertEqual(False, feedback.moving_obstacles[1].hit)

    def test_evaluate_teams_specific_users(self):
        """Tests the evaluation of teams method with specific users."""
        user0 = User.objects.get(username='user0')
        user1 = User.objects.get(username='user1')
        config = MissionConfig.objects.get()

        mission_eval = config.evaluate_teams([user0])

        self.assertEqual(1, len(mission_eval.teams))
        self.assertEqual(user0.username, mission_eval.teams[0].team)

    def assert_non_superuser_data(self, data):
        """Tests non-superuser data is correct."""
        self.assertIn('id', data)
        self.assertEqual(3, data['id'])

        self.assertIn('home_pos', data)
        self.assertIn('latitude', data['home_pos'])
        self.assertIn('longitude', data['home_pos'])
        self.assertEqual(38.0, data['home_pos']['latitude'])
        self.assertEqual(-79.0, data['home_pos']['longitude'])

        self.assertIn('fly_zones', data)
        self.assertEqual(1, len(data['fly_zones']))
        self.assertIn('altitude_msl_min', data['fly_zones'][0])
        self.assertEqual(0.0, data['fly_zones'][0]['altitude_msl_min'])
        self.assertIn('altitude_msl_max', data['fly_zones'][0])
        self.assertEqual(20.0, data['fly_zones'][0]['altitude_msl_max'])
        self.assertIn('boundary_pts', data['fly_zones'][0])
        self.assertEqual(4, len(data['fly_zones'][0]['boundary_pts']))
        self.assertIn('latitude', data['fly_zones'][0]['boundary_pts'][0])
        self.assertEqual(37.0,
                         data['fly_zones'][0]['boundary_pts'][0]['latitude'])
        self.assertIn('longitude', data['fly_zones'][0]['boundary_pts'][0])
        self.assertEqual(-75.0,
                         data['fly_zones'][0]['boundary_pts'][0]['longitude'])
        self.assertIn('order', data['fly_zones'][0]['boundary_pts'][0])
        self.assertEqual(0, data['fly_zones'][0]['boundary_pts'][0]['order'])

        self.assertIn('mission_waypoints', data)
        for waypoint in data['mission_waypoints']:
            self.assertIn('order', waypoint)
            self.assertIn('latitude', waypoint)
            self.assertIn('longitude', waypoint)
            self.assertIn('altitude_msl', waypoint)

        self.assertEqual(2, len(data['mission_waypoints']))
        self.assertEqual(0, data['mission_waypoints'][0]['order'])
        self.assertEqual(38.0, data['mission_waypoints'][0]['latitude'])
        self.assertEqual(-76.0, data['mission_waypoints'][0]['longitude'])
        self.assertEqual(30.0, data['mission_waypoints'][0]['altitude_msl'])

        self.assertEqual(1, data['mission_waypoints'][1]['order'])
        self.assertEqual(38.0, data['mission_waypoints'][1]['latitude'])
        self.assertEqual(-77.0, data['mission_waypoints'][1]['longitude'])
        self.assertEqual(60.0, data['mission_waypoints'][1]['altitude_msl'])

        self.assertIn('search_grid_points', data)
        for point in data['search_grid_points']:
            self.assertIn('order', point)
            self.assertIn('latitude', point)
            self.assertIn('longitude', point)
            self.assertIn('altitude_msl', point)

        self.assertEqual(1, len(data['search_grid_points']))

        self.assertEqual(10, data['search_grid_points'][0]['order'])
        self.assertEqual(38.0, data['search_grid_points'][0]['latitude'])
        self.assertEqual(-79.0, data['search_grid_points'][0]['longitude'])
        self.assertEqual(1000.0, data['search_grid_points'][0]['altitude_msl'])

        self.assertIn('off_axis_target_pos', data)
        self.assertIn('latitude', data['off_axis_target_pos'])
        self.assertIn('longitude', data['off_axis_target_pos'])
        self.assertEqual(38.0, data['off_axis_target_pos']['latitude'])
        self.assertEqual(-79.0, data['off_axis_target_pos']['longitude'])

        self.assertIn('emergent_last_known_pos', data)
        self.assertIn('latitude', data['emergent_last_known_pos'])
        self.assertIn('longitude', data['emergent_last_known_pos'])
        self.assertEqual(38.0, data['emergent_last_known_pos']['latitude'])
        self.assertEqual(-79.0, data['emergent_last_known_pos']['longitude'])

        self.assertIn('air_drop_pos', data)
        self.assertIn('latitude', data['air_drop_pos'])
        self.assertIn('longitude', data['air_drop_pos'])
        self.assertEqual(38.0, data['air_drop_pos']['latitude'])
        self.assertEqual(-79.0, data['air_drop_pos']['longitude'])

    def test_non_superuser_json(self):
        """Conversion to dict for JSON."""
        config = MissionConfig.objects.get()
        data = config.json(is_superuser=False)
        self.assert_non_superuser_data(data)

        self.assertNotIn('stationary_obstacles', data)
        self.assertNotIn('moving_obstacles', data)

    def test_superuser_json(self):
        """Conversion to dict for JSON."""
        config = MissionConfig.objects.get()
        data = config.json(is_superuser=True)
        self.assert_non_superuser_data(data)

        self.assertIn('stationary_obstacles', data)
        self.assertEqual(2, len(data['stationary_obstacles']))
        for obst in data['stationary_obstacles']:
            self.assertIn('latitude', obst)
            self.assertIn('longitude', obst)
            self.assertIn('cylinder_radius', obst)
            self.assertIn('cylinder_height', obst)
        self.assertEqual(10.0,
                         data['stationary_obstacles'][0]['cylinder_height'])
        self.assertEqual(10.0,
                         data['stationary_obstacles'][0]['cylinder_radius'])
        self.assertEqual(38.0, data['stationary_obstacles'][0]['latitude'])
        self.assertEqual(-76.0, data['stationary_obstacles'][0]['longitude'])

        self.assertIn('moving_obstacles', data)
        self.assertEqual(2, len(data['moving_obstacles']))
        for obst in data['moving_obstacles']:
            self.assertIn('speed_avg', obst)
            self.assertIn('sphere_radius', obst)
        self.assertEqual(1.0, data['moving_obstacles'][0]['speed_avg'])
        self.assertEqual(15.0, data['moving_obstacles'][0]['sphere_radius'])

    def test_toKML(self):
        """Test Generation of kml for all mission data"""
        kml = Kml()
        MissionConfig.kml_all(kml=kml)
        data = kml.kml()
        names = [
            'Off Axis',
            'Home Position',
            'Air Drop',
            'Emergent LKP',
            'Search Area',
            'Waypoints',
        ]
        for name in names:
            tag = '<name>{}</name>'.format(name)
            err = 'tag "{}" not found in {}'.format(tag, data)
            self.assertIn(tag, data, err)
