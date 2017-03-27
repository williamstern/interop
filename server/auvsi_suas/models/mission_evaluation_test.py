"""Tests for the mission_evaluation module."""

from django.contrib.auth.models import User
from django.test import TestCase

from auvsi_suas.models import mission_evaluation
from auvsi_suas.models import mission_config


class TestMissionEvaluation(TestCase):
    """Tests the mission_evaluation module."""
    fixtures = ['testdata/sample_mission.json']

    def test_evaluate_teams(self):
        """Tests the evaluation of teams method."""
        user0 = User.objects.get(username='user0')
        user1 = User.objects.get(username='user1')
        config = mission_config.MissionConfig.objects.get()

        mission_eval = mission_evaluation.evaluate_teams(config)

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

        self.assertEqual(1, feedback.judge.flight_time_sec)

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

        self.assertEqual(2, feedback.judge.flight_time_sec)

    def test_evaluate_teams_specific_users(self):
        """Tests the evaluation of teams method with specific users."""
        user0 = User.objects.get(username='user0')
        user1 = User.objects.get(username='user1')
        config = mission_config.MissionConfig.objects.get()

        mission_eval = mission_evaluation.evaluate_teams(config, [user0])

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
