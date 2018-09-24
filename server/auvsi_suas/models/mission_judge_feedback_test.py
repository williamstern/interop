"""Tests for the mission_judge_feedback module."""

import datetime
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.mission_config import MissionConfig
from auvsi_suas.models.mission_judge_feedback import MissionJudgeFeedback
from auvsi_suas.models.waypoint import Waypoint
from django.contrib.auth.models import User
from django.test import TestCase


class TestMissionJudgeFeedback(TestCase):
    def setUp(self):
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
        config.off_axis_odlc_pos = pos
        config.air_drop_pos = pos
        config.save()
        config.mission_waypoints.add(wpt)
        config.search_grid_points.add(wpt)
        config.save()

        user = User.objects.create_user('user', 'email@example.com', 'pass')

        self.feedback = MissionJudgeFeedback(
            mission=config,
            user=user,
            flight_time=datetime.timedelta(seconds=1),
            post_process_time=datetime.timedelta(seconds=2),
            used_timeout=True,
            min_auto_flight_time=True,
            safety_pilot_takeovers=3,
            waypoints_captured=5,
            out_of_bounds=6,
            unsafe_out_of_bounds=7,
            things_fell_off_uas=False,
            crashed=False,
            air_delivery_accuracy_ft=8,
            operational_excellence_percent=9)
        self.feedback.save()

    def test_proto(self):
        """Tests proto()."""
        pb = self.feedback.proto()

        self.assertAlmostEqual(1, pb.flight_time_sec)
        self.assertAlmostEqual(2, pb.post_process_time_sec)
        self.assertTrue(pb.used_timeout)
        self.assertTrue(pb.min_auto_flight_time)
        self.assertEqual(3, pb.safety_pilot_takeovers)
        self.assertEqual(5, pb.waypoints_captured)
        self.assertEqual(6, pb.out_of_bounds)
        self.assertEqual(7, pb.unsafe_out_of_bounds)
        self.assertFalse(pb.things_fell_off_uas)
        self.assertFalse(pb.crashed)
        self.assertAlmostEqual(8, pb.air_delivery_accuracy_ft)
        self.assertAlmostEqual(9, pb.operational_excellence_percent)

        self.feedback.air_delivery_accuracy_ft = None
        pb = self.feedback.proto()

        self.assertFalse(pb.HasField('air_delivery_accuracy_ft'))
