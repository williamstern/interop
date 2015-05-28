"""Tests for the obstacles module."""

import time
import json
import logging
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import ObstacleAccessLog
from auvsi_suas.models import StationaryObstacle
from auvsi_suas.models import Waypoint
from auvsi_suas.models import moving_obstacle_test
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class TestGetObstaclesView(TestCase):
    """Tests the getObstacles view."""

    def setUp(self):
        """Sets up the client, obstacle URL, obstacles, and user."""
        # Setup user
        self.user = User.objects.create_user(
                'testuser', 'testemail@x.com', 'testpass')
        self.user.save()
        # Setup the obstacles
        for path in moving_obstacle_test.TESTDATA_MOVOBST_PATHS:
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
        if not settings.TEST_ENABLE_LOADTEST:
            return

        client = self.client
        loginUrl = self.loginUrl
        obstUrl = self.obstUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        total_ops = 0
        start_t = time.clock()
        while time.clock() - start_t < settings.TEST_LOADTEST_TIME:
            client.get(obstUrl)
            total_ops += 1
        end_t = time.clock()
        total_t = end_t - start_t
        op_rate = total_ops / total_t

        print 'Obstacle Info Rate (%f)' % op_rate
        self.assertGreaterEqual(
                op_rate, settings.TEST_LOADTEST_INTEROP_MIN_RATE)


