import os
import requests
import unittest

from . import Client, InteropError, Telemetry

# These tests run against a real interop server.
# Set these environmental variables to the proper values
# if the defaults are not correct.
server = os.getenv('TEST_INTEROP_SERVER', 'http://localhost')
username = os.getenv('TEST_INTEROP_USER', 'testuser')
password = os.getenv('TEST_INTEROP_PASS', 'testpass')


class TestClient(unittest.TestCase):
    """Test the Client class.
    The Client class is a very thin wrapper, so there is very little to test.
    """

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

    def test_post_telemetry(self):
        """Test sending some telemetry."""
        c = Client(server, username, password)
        t = Telemetry(latitude=38,
                      longitude=76,
                      altitude_msl=100,
                      uas_heading=90)

        # Raises an exception on error.
        c.post_telemetry(t)

    def test_post_bad_telemetry(self):
        """Test sending some (incorrect) telemetry."""
        c = Client(server, username, password)

        with self.assertRaises(InteropError):
            t = Telemetry(latitude=38,
                          longitude=76,
                          altitude_msl=100,
                          uas_heading=90)

            # The Telemetry constructor prevents us from passing invalid
            # values, but we can still screw things up in an update
            t.latitude = 'baz'

            c.post_telemetry(t)

        with self.assertRaises(AttributeError):
            t = {
                'latitude': 38,
                'longitude': 76,
                'altitude_msl': 100,
                'uas_heading': 90
            }

            # We only accept Telemetry objects (or objects that behave like
            # Telemetry, not dicts.
            c.post_telemetry(t)
