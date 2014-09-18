from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
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


class TestHaversine(TestCase):
    """Tests the haversine code correctness."""

    def distance_close_enough(self, self, distance_actual, distance_received):
        """Determines whether the km distances given are close enough.

        Args:
            distance_actual: The actual distance.
            distance_received: The distanced received from haversine code.
        Returns:
            True if the distances are close enoug, False otherwise.
        """
        # TODO

    def evaluate_input(self, lon1, lat1, lon2, lat2, distance_actual):
        """Evaluates the haversine code for the given input.

        Args:
            lon1, lat1, lon2, lat2: Values for haversine code.
            distance_actual: The actual distance which should be returned.
        Returns:
            True if the haversine code returned the correct value, False
            otherwise.
        """
        # TODO

    def test_zero_distance(self):
        """Tests various latitudes and longitudes which have zero distance."""
        # TODO

    def test_hemisphere_distances(self):
        """Tests distances in each hemisphere."""
        # TODO

    def test_competition_distances(self):
        """Tests distances representative of competition amounts."""
        # TODO


def TestGpsPositionModel(TestCase):
    """Tests the GpsPosition model."""

    def test_kilometersToFeet_zero(self):
        """Tests a conversion with value zero."""
        # TODO

    def test_kilometersToFeet_competition_amounts(self):
        """Tests a conversion using amounts relative to the competition."""
        # TODO

    def test_distanceTo_zero(self):
        """Tests distance calc for same position."""
        # TODO

    def test_distanceTo_competition_amounts(self):
        """Tests distance calc for competition amounts."""
        # TODO


def TestAerialPositionModel(TestCase):
    """Tests the AerialPosition model."""

    def test_distanceTo_zero(self):
        """Tests distance calc for same position."""
        # TODO

    def test_distanceTo_competition_amounts(self):
        """Tests distance calc for competition amounts."""
        # TODO


def TestWaypointModel(TestCase):
    """Tests the Waypoint model."""

    def test_distanceTo_zero(self):
        """Tests distance calc for same positions."""
        # TODO

    def test_distanceTo_competition_amounts(self):
        """Tests distance calc for competition amounts."""
        # TODO


def TestServerInfoModel(TestCase):
    """Tests the ServerInfo model."""

    def test_toJSON(self):
        """Tests the JSON serialization method."""
        # TODO


def TestStationaryObstacleModel(TestCase):
    """Tests the StationaryObstacle model."""

    def test_toJSON(self):
        """Tests the JSON serialization model."""
        # TODO


def TestMovingObstacle(TestCase):
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
