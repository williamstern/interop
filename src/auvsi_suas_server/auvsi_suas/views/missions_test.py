"""Tests for the missions module."""

import json
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone


login_url = reverse('auvsi_suas:login')
missions_url = reverse('auvsi_suas:missions')


class TestMissionsViewLoggedOut(TestCase):

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        response = self.client.get(missions_url)
        self.assertGreaterEqual(response.status_code, 300)

class TestMissionsViewCommon(TestCase):
    """Common test setup"""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
                'superuser', 'email@example.com', 'superpass')
        self.superuser.save()

        # Login
        response = self.client.post(login_url, {
            'username': 'superuser',
            'password': 'superpass'
        })
        self.assertEqual(200, response.status_code)

class TestMissionsViewBasic(TestMissionsViewCommon):
    """Tests the missions view with minimal data."""

    def test_normal_user(self):
        """Normal users not allowed access."""
        user = User.objects.create_user(
                'testuser', 'email@example.com', 'testpass')
        user.save()

        # Login
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(200, response.status_code)

        response = self.client.get(missions_url)
        self.assertGreaterEqual(response.status_code, 300)

    def test_post(self):
        """POST not allowed"""
        response = self.client.post(missions_url)
        self.assertEqual(400, response.status_code)

    def test_no_missions(self):
        """No missions results in empty list."""
        response = self.client.get(missions_url)
        self.assertEqual(200, response.status_code)

        self.assertEqual([], json.loads(response.content))

class TestMissionsViewSampleMission(TestMissionsViewCommon):
    """Tests the missions view with sample mission."""

    fixtures = ['testdata/sample_mission.json']

    def test_correct_json(self):
        """Response JSON is properly formatted."""
        response = self.client.get(missions_url)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        self.assertEqual(1, len(data))

        self.assertIn('id', data[0])
        self.assertEqual(3, data[0]['id'])

        self.assertIn('home_pos', data[0])
        self.assertIn('latitude', data[0]['home_pos'])
        self.assertIn('longitude', data[0]['home_pos'])
        self.assertEqual(10.0, data[0]['home_pos']['latitude'])
        self.assertEqual(100.0, data[0]['home_pos']['longitude'])

        self.assertIn('mission_waypoints_dist_max', data[0])
        self.assertEqual(10.0, data[0]['mission_waypoints_dist_max'])

        self.assertIn('mission_waypoints', data[0])
        for waypoint in data[0]['mission_waypoints']:
            self.assertIn('id', waypoint)
            self.assertIn('latitude', waypoint)
            self.assertIn('longitude', waypoint)
            self.assertIn('altitude_msl', waypoint)
            self.assertIn('order', waypoint)

        self.assertEqual(2, len(data[0]['mission_waypoints']))

        self.assertEqual(155, data[0]['mission_waypoints'][0]['id'])
        self.assertEqual(38.0, data[0]['mission_waypoints'][0]['latitude'])
        self.assertEqual(-76.0, data[0]['mission_waypoints'][0]['longitude'])
        self.assertEqual(30.0, data[0]['mission_waypoints'][0]['altitude_msl'])
        self.assertEqual(0, data[0]['mission_waypoints'][0]['order'])

        self.assertEqual(156, data[0]['mission_waypoints'][1]['id'])
        self.assertEqual(38.0, data[0]['mission_waypoints'][1]['latitude'])
        self.assertEqual(-76.0, data[0]['mission_waypoints'][1]['longitude'])
        self.assertEqual(60.0, data[0]['mission_waypoints'][1]['altitude_msl'])
        self.assertEqual(1, data[0]['mission_waypoints'][1]['order'])

        self.assertIn('search_grid_points', data[0])
        for point in data[0]['search_grid_points']:
            self.assertIn('id', point)
            self.assertIn('latitude', point)
            self.assertIn('longitude', point)
            self.assertIn('altitude_msl', point)
            self.assertIn('order', point)

        self.assertEqual(1, len(data[0]['search_grid_points']))

        self.assertEqual(150, data[0]['search_grid_points'][0]['id'])
        self.assertEqual(10.0, data[0]['search_grid_points'][0]['latitude'])
        self.assertEqual(100.0, data[0]['search_grid_points'][0]['longitude'])
        self.assertEqual(1000.0, data[0]['search_grid_points'][0]['altitude_msl'])
        self.assertEqual(10, data[0]['search_grid_points'][0]['order'])

        self.assertIn('emergent_last_known_pos', data[0])
        self.assertIn('latitude', data[0]['emergent_last_known_pos'])
        self.assertIn('longitude', data[0]['emergent_last_known_pos'])
        self.assertEqual(10.0, data[0]['emergent_last_known_pos']['latitude'])
        self.assertEqual(100.0, data[0]['emergent_last_known_pos']['longitude'])

        self.assertIn('off_axis_target_pos', data[0])
        self.assertIn('latitude', data[0]['off_axis_target_pos'])
        self.assertIn('longitude', data[0]['off_axis_target_pos'])
        self.assertEqual(10.0, data[0]['off_axis_target_pos']['latitude'])
        self.assertEqual(100.0, data[0]['off_axis_target_pos']['longitude'])

        self.assertIn('sric_pos', data[0])
        self.assertIn('latitude', data[0]['sric_pos'])
        self.assertIn('longitude', data[0]['sric_pos'])
        self.assertEqual(10.0, data[0]['sric_pos']['latitude'])
        self.assertEqual(100.0, data[0]['sric_pos']['longitude'])

        self.assertIn('ir_primary_target_pos', data[0])
        self.assertIn('latitude', data[0]['ir_primary_target_pos'])
        self.assertIn('longitude', data[0]['ir_primary_target_pos'])
        self.assertEqual(10.0, data[0]['ir_primary_target_pos']['latitude'])
        self.assertEqual(100.0, data[0]['ir_primary_target_pos']['longitude'])

        self.assertIn('ir_secondary_target_pos', data[0])
        self.assertIn('latitude', data[0]['ir_secondary_target_pos'])
        self.assertIn('longitude', data[0]['ir_secondary_target_pos'])
        self.assertEqual(10.0, data[0]['ir_secondary_target_pos']['latitude'])
        self.assertEqual(100.0, data[0]['ir_secondary_target_pos']['longitude'])

        self.assertIn('air_drop_pos', data[0])
        self.assertIn('latitude', data[0]['air_drop_pos'])
        self.assertIn('longitude', data[0]['air_drop_pos'])
        self.assertEqual(10.0, data[0]['air_drop_pos']['latitude'])
        self.assertEqual(100.0, data[0]['air_drop_pos']['longitude'])
