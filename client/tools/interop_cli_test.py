import os
import subprocess
import time
import unittest
from pymavlink import mavutil

from interop import Telemetry

# TODO(pmtischler): Add tests for other interop_cli use cases.


class TestMavlink(unittest.TestCase):
    """Tests proxying MAVLink packets."""

    def setUp(self):
        """Creates a playback and forward of MAVLink packets."""
        # Create input and output logs to simulate a source.
        log_filepath = os.path.join(
            os.path.dirname(__file__), "testdata/mav.tlog")
        self.mlog = mavutil.mavlink_connection(log_filepath)
        self.mout = mavutil.mavlink_connection('127.0.0.1:14550', input=False)
        # Start the forwarding on the CLI.
        cli_path = os.path.join(os.path.dirname(__file__), "interop_cli.py")
        self.forward = subprocess.Popen(
            [cli_path, '--url', 'http://localhost:8000', '--username',
             'testuser', '--password', 'testpass', 'mavlink', '--device',
             '127.0.0.1:14550'])
        time.sleep(1)  # Allow time to start forward.

    def tearDown(self):
        """Stops any subprocesses."""
        if self.forward.returncode is None:
            self.forward.terminate()

    def assertForwardAlive(self):
        """Asserts the forward process is alive."""
        self.forward.poll()
        self.assertIsNone(self.forward.returncode)

    def test_proxy(self):
        """Checks that proxying doesn't die."""
        # Forward all proxy messages.
        while True:
            self.assertForwardAlive()
            msg = self.mlog.recv_match()
            if msg is None:
                break
            self.mout.write(msg.get_msgbuf())
        # Ensure proxy still alive for 5s.
        start = time.time()
        while time.time() - start < 5:
            self.assertForwardAlive()
            time.sleep(0.1)
