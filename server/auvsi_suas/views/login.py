"""Interoperability login view."""

import logging
from auvsi_suas.proto.interop_api_pb2 import Credentials
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
        creds = Credentials()
        try:
            json_format.Parse(request.body, creds)
        except Exception as e:
            msg = 'Failed to parse request. Error: %s' % str(e)
            logging.warning(msg)
            logging.debug(request)
            return HttpResponseBadRequest(msg)

        if not creds.HasField('username') or not creds.HasField('password'):
            msg = 'Request missing fields.'
            logging.warning(msg)
            logging.debug(request)
            return HttpResponseBadRequest(msg)

        user = authenticate(username=creds.username, password=creds.password)
        if user is not None and user.is_active:
            # Successful authentication with active user, login
            login(request, user)
            msg = 'User logged in: %s' % user.username
            logger.info(msg)
            return HttpResponse(msg)
        else:
            # Invalid user credentials, invalid request
            msg = 'Invalid credentials in request. Could not log in.'
            logger.warning(msg)
            logger.debug(request)
            return HttpResponse(msg, status=401)
