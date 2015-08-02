import os
import requests
import unittest

from . import Client, InteropError, Telemetry

# These tests run against a real interop server.
# The server be loaded with the data from the test fixture in
# server/fixtures/test_fixture.yaml.

# Set these environmental variables to the proper values
# if the defaults are not correct.
server = os.getenv('TEST_INTEROP_SERVER', 'http://localhost')
username = os.getenv('TEST_INTEROP_USER', 'testuser')
password = os.getenv('TEST_INTEROP_PASS', 'testpass')


class TestClientLoggedOut(unittest.TestCase):
    """Test the portions of the Client class used before login."""

    def test_login(self):
        """Simple login test."""
        # Simply creating a Client causes a login.
        # If it doesn't raise an exception, it worked!
        Client(server, username, password)

    def test_bad_login(self):
        """Bad login raises exception"""
        with self.assertRaises(InteropError):
            Client(server, "foo", "bar")

    def test_timeout(self):
        """Test connection timeout"""
        with self.assertRaises(requests.Timeout):
            # We are assuming that there is no machine at this address
            Client("http://10.255.255.255", username, password, timeout=0.1)


class TestClient(unittest.TestCase):
    """Test the Client class.
    The Client class is a very thin wrapper, so there is very little to test.
    """

    def setUp(self):
        """Create a logged in Client."""
        self.client = Client(server, username, password)

    def test_get_server_info(self):
        """Test getting server info."""
        info = self.client.get_server_info()

        # There isn't a whole lot to test. The fact that the call
        # didn't raise an exception is a good sign.
        self.assertEqual("Hello World!", info.message)
        # TODO(prattmic): check these values once the timestamps come
        # in a defined format.
        self.assertIsNotNone(info.message_timestamp)
        self.assertIsNotNone(info.server_time)

    def test_post_telemetry(self):
        """Test sending some telemetry."""
        t = Telemetry(latitude=38,
                      longitude=-76,
                      altitude_msl=100,
                      uas_heading=90)

        # Raises an exception on error.
        self.client.post_telemetry(t)

    def test_post_bad_telemetry(self):
        """Test sending some (incorrect) telemetry."""
        with self.assertRaises(InteropError):
            t = Telemetry(latitude=38,
                          longitude=-76,
                          altitude_msl=100,
                          uas_heading=90)

            # The Telemetry constructor prevents us from passing invalid
            # values, but we can still screw things up in an update
            t.latitude = 'baz'

            self.client.post_telemetry(t)

        with self.assertRaises(AttributeError):
            t = {
                'latitude': 38,
                'longitude': -76,
                'altitude_msl': 100,
                'uas_heading': 90
            }

            # We only accept Telemetry objects (or objects that behave like
            # Telemetry, not dicts.
            self.client.post_telemetry(t)
