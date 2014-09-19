from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import haversine
from auvsi_suas.models import kilometersToFeet
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import Obstacle
from auvsi_suas.models import ObstacleAccessLog
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from auvsi_suas.models import StationaryObstacle
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import Waypoint
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


# (lon1, lat1, lon2, lat2, dist_actual)
TESTDATA_ZERO_DIST = [
    (0, 0, 0, 0, 0),
    (1, 1, 1, 1, 0),
    (-1, -1, -1, -1, 0),
    (1, -1, 1, -1, 0),
    (-1, 1, -1, 1, 0),
    (76, 42, 76, 42, 0),
    (-76, 42, -76, 42, 0)
]
TESTDATA_HEMISPHERE_DIST = [
    (-73, 40, -74, 41, 139.6886345468666),
    (73, 40, 74, 41, 139.6886345468667),
    (73, -40, 74, -41, 139.6886345468667),
    (-73, -40, -74, -41, 139.68863454686704)
]
TESTDATA_COMPETITION_DIST = [
    (-76.428709, 38.145306, -76.426375, 38.146146, 0.22446),
    (-76.428537, 38.145399, -76.427818, 38.144686, 0.10045),
    (-76.434261, 38.142471, -76.418876, 38.147838, 1.46914)
]

# (km, ft_actual)
TESTDATA_KM_TO_FT = [
    (0, 0),
    (1, 3280.84),
    (1.5, 4921.26),
    (100, 328084)
]

# (lon1, lat1, alt1, lon2, lat2, alt2, dist_actual)
TESTDATA_ZERO_3D_DIST = [
    (0, 0, 0, 0, 0, 0, 0),
    (1, 2, 3, 1, 2, 3, 0),
    (-30, 30, 100, -30, 30, 100, 0)
]
TESTDATA_COMPETITION_3D_DIST = [
    (-76.428709, 38.145306, 0, -76.426375, 38.146146, 0, 0.22446),
    (-76.428537, 38.145399, 0, -76.427818, 38.144686, 100, 0.10497),
    (-76.434261, 38.142471, 100, -76.418876, 38.147838, 800, 1.48455)
]


class TestHaversine(TestCase):
    """Tests the haversine code correctness."""

    def distance_close_enough(self, distance_actual, distance_received):
        """Determines whether the km distances given are close enough."""
        distance_thresh = 0.003048  # 10 feet in km
        return abs(distance_actual - distance_received) <= distance_thresh

    def evaluate_input(self, lon1, lat1, lon2, lat2, distance_actual):
        """Evaluates the haversine code for the given input."""
        distance_received = haversine(lon1, lat1, lon2, lat2)
        return self.distance_close_enough(distance_actual, distance_received)

    def evaluate_inputs(self, input_output_list):
        """Evaluates a list of inputs and outputs."""
        for (lon1, lat1, lon2, lat2, distance_actual) in input_output_list:
            if not self.evaluate_input(lon1, lat1, lon2, lat2, distance_actual):
                return False
        return True

    def test_zero_distance(self):
        """Tests various latitudes and longitudes which have zero distance."""
        self.assertTrue(self.evaluate_inputs(
            TESTDATA_ZERO_DIST))

    def test_hemisphere_distances(self):
        """Tests distances in each hemisphere."""
        self.assertTrue(self.evaluate_inputs(
            TESTDATA_HEMISPHERE_DIST))

    def test_competition_distances(self):
        """Tests distances representative of competition amounts."""
        self.assertTrue(self.evaluate_inputs(
            TESTDATA_COMPETITION_DIST))


class TestKilometersToFeet(TestCase):
    """Tests the conversion from kilometers to feet."""

    def evaluate_conversion(self, km, ft_actual):
        """Tests the conversion of the given input to feet."""
        convert_thresh = 10.0
        return abs(kilometersToFeet(km) - ft_actual) < convert_thresh

    def test_km_to_ft(self):
        """Performs a data-driven test of the conversion."""
        for (km, ft_actual) in TESTDATA_KM_TO_FT:
            self.assertTrue(self.evaluate_conversion(km, ft_actual))


class TestGpsPositionModel(TestCase):
    """Tests the GpsPosition model."""

    def eval_distanceTo_input(self, lon1, lat1, lon2, lat2, distance_actual):
        """Evaluates the distanceTo functionality for the given inputs."""
        wpt1 = GpsPosition()
        wpt1.latitude = lat1
        wpt1.longitude = lon1
        wpt2 = GpsPosition()
        wpt2.latitude = lat2
        wpt2.longitude = lon2
        dist12 = wpt1.distanceTo(wpt2)
        dist21 = wpt2.distanceTo(wpt1)
        dist_actual_ft = kilometersToFeet(distance_actual)
        diffdist12 = abs(dist12 - dist_actual_ft)
        diffdist21 = abs(dist21 - dist_actual_ft)
        dist_thresh = 10.0
        return diffdist12 <= dist_thresh and diffdist21 <= dist_thresh

    def eval_distanceTo_inputs(self, input_output_list):
        """Evaluates the distanceTo function on various inputs."""
        for (lon1, lat1, lon2, lat2, distance_actual) in input_output_list:
            if not self.eval_distanceTo_input(lon1, lat1, lon2, lat2,
                    distance_actual):
                return False
        return True

    def test_distanceTo_zero(self):
        """Tests distance calc for same position."""
        self.assertTrue(self.eval_distanceTo_inputs(
            TESTDATA_ZERO_DIST))

    def test_distanceTo_competition_amounts(self):
        """Tests distance calc for competition amounts."""
        self.assertTrue(self.eval_distanceTo_inputs(
            TESTDATA_COMPETITION_DIST))


class TestAerialPositionModel(TestCase):
    """Tests the AerialPosition model."""

    def eval_distanceTo_input(self, lon1, lat1, alt1, lon2, lat2, alt2,
            dist_actual):
        """Evaluates the distanceTo calc with the given inputs."""
        pos1 = AerialPosition()
        pos1.gps_position = GpsPosition()
        pos1.gps_position.latitude = lat1
        pos1.gps_position.longitude = lon1
        pos1.msl_altitude = alt1
        pos2 = AerialPosition()
        pos2.gps_position = GpsPosition()
        pos2.gps_position.latitude = lat2
        pos2.gps_position.longitude = lon2
        pos2.msl_altitude = alt2
        dist12 = pos1.distanceTo(pos2)
        dist21 = pos2.distanceTo(pos1)
        dist_actual_ft = kilometersToFeet(dist_actual)
        diffdist12 = abs(dist12 - dist_actual_ft)
        diffdist21 = abs(dist21 - dist_actual_ft)
        dist_thresh = 10.0
        return diffdist12 <= dist_thresh and diffdist21 <= dist_thresh

    def eval_distanceTo_inputs(self, input_output_list):
        """Evaluates the distanceTo calc with the given input list."""
        for (lon1, lat1, alt1,
                lon2, lat2, alt2, dist_actual) in input_output_list:
            if not self.eval_distanceTo_input(lon1, lat1, alt1, lon2, lat2,
                    alt2, dist_actual):
                return False
        return True

    def test_distanceTo_zero(self):
        """Tests distance calc for same position."""
        self.assertTrue(self.eval_distanceTo_inputs(
            TESTDATA_ZERO_3D_DIST))

    def test_distanceTo_competition_amounts(self):
        """Tests distance calc for competition amounts."""
        self.assertTrue(self.eval_distanceTo_inputs(
            TESTDATA_COMPETITION_3D_DIST))


class TestServerInfoModel(TestCase):
    """Tests the ServerInfo model."""

    def test_toJSON(self):
        """Tests the JSON serialization method."""
        # TODO


class TestStationaryObstacleModel(TestCase):
    """Tests the StationaryObstacle model."""

    def test_toJSON(self):
        """Tests the JSON serialization model."""
        # TODO


class TestMovingObstacle(TestCase):
    """Tests the MovingObstacle model."""

    def test_getWaypointTravelTime_invalid_inputs(self):
        """Tests proper invalid input handling."""
        # TODO

    def test_getWaypointTravelTime_competition_amounts(self):
        """Tests travel time calc for competition amounts."""
        # TODO

    def test_getPosition_no_waypoints(self):
        """Tests position calc on no-waypoint."""
        # TODO

    def test_getPosition_one_waypoint(self):
        """Tests position calc on single waypoints."""
        # TODO

    def test_getPosition_within_bounds(self):
        """Tests position calc staying within reasonable bounds."""
        # TODO

    def test_getPosition_waypoints_same_position(self):
        """Tests position calc with waypoints on the same position."""
        # TODO

    def test_getPosition_waypoints_plot(self):
        """Tests position calculation by saving plots of calculation.

        Saves plots to /tmp/auvsi_suas-MovingObstacle-getPosition/x.jpg. On
        each run it first deletes the existing folder. This requires manual
        inspection to validate correctness.
        """
        # TODO

    def test_toJSON(self):
        """Tests the JSON serialization model."""
        # TODO


class TestLoginUserView(TestCase):
    """Tests the loginUser view."""

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        # TODO

    def test_invalid_credentials(self):
        """Tests invalid credentials for login."""
        # TODO

    def test_correct_credentials(self):
        """Tests correct credentials for login."""
        # TODO


class TestGetServerInfoView(TestCase):
    """Tests the getServerInfo view."""

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        # TODO

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        # TODO

    def test_correct_log_and_response(self):
        """Tests that access is logged and returns valid response."""
        # TODO

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        # TODO


class TestGetObstaclesView(TestCase):
    """Tests the getObstacles view."""

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        # TODO

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        # TODO

    def test_correct_log_and_response(self):
        """Tests that access is logged and returns valid response."""
        # TODO

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        # TODO


class TestPostUasPosition(TestCase):
    """Tests the postUasPosition view."""

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        # TODO

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        # TODO

    def test_invalid_request_values(self):
        """Tests by specifying correct parameters with invalid values."""
        # TODO

    def test_upload_and_store(self):
        """Tests correct upload and storage of data."""
        # TODO

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        # TODO
