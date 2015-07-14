"""Core interoperability client module

This module provides a Python interface to the SUAS interoperability API.

See README.md for more details."""

import requests


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

    def post(self, uri, **kwargs):
        """POST request to server.

        Args:
            uri: Server URI to access (without base URL)
            **kwargs: Arguments to requests.Session.post method

        Raises:
            requests.HTTPError: Error from server
            requests.Timeout: Request timeout
        """
        r = self.session.post(self.url + uri, timeout=self.timeout, **kwargs)
        # TODO(prattmic): Custom exception types, including the server error
        # message.
        r.raise_for_status()

    def post_telemetry(self, telem):
        """POST new telemetry.

        Args:
            telem: Telemetry object containing telemetry state.
        """
        self.post('/api/interop/uas_telemetry', data=telem.serialize())
