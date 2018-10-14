"""Interoperability login view."""

import logging
from auvsi_suas.proto.account_pb2 import LoginRequest
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.generic import View
from google.protobuf import json_format

logger = logging.getLogger(__name__)


class Login(View):
    """Logs the user in with a POST request using the given parameters."""

    def post(self, request):
        request_proto = LoginRequest()
        try:
            json_format.Parse(request.body, request_proto)
        except:
            logging.warning('Failed to parse request.')
            return HttpResponseBadRequest('Failed to parse request.')

        if (not request_proto.HasField('username') or
                not request_proto.HasField('password')):
            logging.warning('Missing fields in request.')
            return HttpResponseBadRequest(
                'Missing fields in request. Both username and password required.'
            )

        user = authenticate(
            username=request_proto.username, password=request_proto.password)
        if user is not None and user.is_active:
            # Successful authentication with active user, login
            login(request, user)
            logger.info('User logged in: %s.' % user.username)
            return HttpResponse('Login Successful.')
        else:
            # Invalid user credentials, invalid request
            logger.warning('Invalid credentials in login request.')
            logger.debug(request)
            return HttpResponse('Invalid Credentials.', status=401)
