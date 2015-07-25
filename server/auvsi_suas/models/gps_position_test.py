"""Tests for the gps_position model."""

from auvsi_suas.models import GpsPosition
from django.test import TestCase


class TestGpsPositionModel(TestCase):
    """Tests the GpsPosition model."""

    def test_unicode(self):
        """Tests the unicode method executes."""
        pos = GpsPosition(latitude=10, longitude=100)
        pos.save()

        pos.__unicode__()

    def assertDistanceEqual(self, pos1, pos2, dist, threshold=10):
        """GpsPosition distances are within threshold (ft)."""
        self.assertAlmostEqual(pos1.distance_to(pos2), dist, delta=threshold)
        self.assertAlmostEqual(pos2.distance_to(pos1), dist, delta=threshold)

    def evaluate_inputs(self, io_list):
        """Evaluates the distance_to calc with the given input list."""
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
            (0,      0,    0,    0,    0),
            (1,      1,    1,    1,    0),
            (-1,     -1,   -1,   -1,   0),
            (1,      -1,   1,    -1,   0),
            (-1,     1,    -1,   1,    0),
            (76,     42,   76,   42,   0),
            (-76,    42,   -76,  42,   0),
        ])  # yapf: disable

    def test_distance_competition_amounts(self):
        """Tests distance calc for competition amounts."""
        self.evaluate_inputs([
            # (lon1,     lat1,      lon2,       lat2,      dist_actual)
            (-76.428709, 38.145306, -76.426375, 38.146146, 736.4),
            (-76.428537, 38.145399, -76.427818, 38.144686, 329.6),
            (-76.434261, 38.142471, -76.418876, 38.147838, 4820.0),
        ])  # yapf: disable
