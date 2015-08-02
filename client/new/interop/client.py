"""Core interoperability client module

This module provides a Python interface to the SUAS interoperability API.

See README.md for more details."""

import requests

from .exceptions import InteropError
from .types import ServerInfo, StationaryObstacle, MovingObstacle


class Client(object):
    """Client provides authenticated access to the endpoints of the
    interoperability API.
    """

    def __init__(self, url, username, password, timeout=1):
        """Create a new Client and login.

        Args:
            url: Base URL of interoperability server
                (e.g., http://localhost:8000)
            username: Interoperability username
            password: Interoperability password
            timeout: Individual session request timeout (seconds)
        """
        self.url = url
        self.timeout = timeout

        self.session = requests.Session()

        # All endpoints require authentication, so always
        # login.
        self.post('/api/login',
                  data={'username': username,
                        'password': password})

    def get(self, uri, **kwargs):
        """GET request to server.

        Args:
            uri: Server URI to access (without base URL)
            **kwargs: Arguments to requests.Session.get method

        Raises:
            InteropError: Error from server
            requests.Timeout: Request timeout
        """
        r = self.session.get(self.url + uri, timeout=self.timeout, **kwargs)
        if not r.ok:
            raise InteropError(r)
        return r

    def post(self, uri, **kwargs):
        """POST request to server.

        Args:
            uri: Server URI to access (without base URL)
            **kwargs: Arguments to requests.Session.post method

        Raises:
            InteropError: Error from server
            requests.Timeout: Request timeout
        """
        r = self.session.post(self.url + uri, timeout=self.timeout, **kwargs)
        if not r.ok:
            raise InteropError(r)

    def get_server_info(self):
        """GET server information, to be displayed to judges.

        Returns:
            ServerInfo object

        Raises:
            InteropError: Error from server. Note that you may receive this
                error if the server has no message configured.
            requests.Timeout: Request timeout
            ValueError or AttributeError: Malformed response from server
        """
        r = self.get('/api/interop/server_info')
        d = r.json()

        return ServerInfo(
            message=d['server_info']['message'],
            message_timestamp=d['server_info']['message_timestamp'],
            server_time=d['server_time'])

    def post_telemetry(self, telem):
        """POST new telemetry.

        Args:
            telem: Telemetry object containing telemetry state.

        Raises:
            InteropError: Error from server
            requests.Timeout: Request timeout
        """
        self.post('/api/interop/uas_telemetry', data=telem.serialize())

    def get_obstacles(self):
        """GET obstacles.

        Returns:
            List of StationaryObstacles and list of MovingObstacles.
                i.e., ([StationaryObstacle], [MovingObstacles])

        Raises:
            InteropError: Error from server
            requests.Timeout: Request timeout
            ValueError or AttributeError: Malformed response from server
        """
        r = self.get('/api/interop/obstacles')
        d = r.json()

        stationary = []
        for o in d['stationary_obstacles']:
            s = StationaryObstacle(latitude=o['latitude'],
                                   longitude=o['longitude'],
                                   cylinder_radius=o['cylinder_radius'],
                                   cylinder_height=o['cylinder_height'])
            stationary.append(s)

        moving = []
        for o in d['moving_obstacles']:
            m = MovingObstacle(latitude=o['latitude'],
                               longitude=o['longitude'],
                               altitude_msl=o['altitude_msl'],
                               sphere_radius=o['sphere_radius'])
            moving.append(m)

        return stationary, moving
