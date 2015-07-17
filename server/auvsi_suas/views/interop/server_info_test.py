"""Tests for the server_info module."""

import time
import json
import logging
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class TestGetServerInfoView(TestCase):
    """Tests the getServerInfo view."""

    def setUp(self):
        """Sets up the client, server info URL, and user."""
        self.user = User.objects.create_user('testuser', 'testemail@x.com',
                                             'testpass')
        self.user.save()
        self.info = ServerInfo()
        self.info.team_msg = 'test message'
        self.info.save()
        self.client = Client()
        self.loginUrl = reverse('auvsi_suas:login')
        self.infoUrl = reverse('auvsi_suas:server_info')
        logging.disable(logging.CRITICAL)

    def test_not_authenticated(self):
        """Tests requests that have not yet been authenticated."""
        client = self.client
        infoUrl = self.infoUrl

        response = client.get(infoUrl)
        self.assertEqual(response.status_code, 400)

    def test_invalid_request(self):
        """Tests an invalid request by mis-specifying parameters."""
        client = self.client
        loginUrl = self.loginUrl
        infoUrl = self.infoUrl

        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})
        response = client.post(infoUrl)
        self.assertEqual(response.status_code, 400)

    def test_correct_log_and_response(self):
        """Tests that access is logged and returns valid response."""
        client = self.client
        loginUrl = self.loginUrl
        infoUrl = self.infoUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        response = client.get(infoUrl)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ServerInfoAccessLog.objects.all()), 1)
        access_log = ServerInfoAccessLog.objects.all()[0]
        self.assertEqual(access_log.user, self.user)
        json_data = json.loads(response.content)
        self.assertTrue('server_info' in json_data)
        self.assertTrue('server_time' in json_data)

    def test_loadtest(self):
        """Tests the max load the view can handle."""
        if not settings.TEST_ENABLE_LOADTEST:
            return

        client = self.client
        loginUrl = self.loginUrl
        infoUrl = self.infoUrl
        client.post(loginUrl, {'username': 'testuser', 'password': 'testpass'})

        total_ops = 0
        start_t = time.clock()
        while time.clock() - start_t < settings.TEST_LOADTEST_TIME:
            client.get(infoUrl)
            total_ops += 1
        end_t = time.clock()
        total_t = end_t - start_t
        op_rate = total_ops / total_t

        print 'Server Info Rate (%f)' % op_rate
        self.assertGreaterEqual(
            op_rate, settings.TEST_LOADTEST_INTEROP_MIN_RATE)
