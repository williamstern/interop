"""Interoperability server info view."""

import datetime
import json
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from auvsi_suas.views import logger
from django.core.cache import cache
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError


def server_info(request):
    """Gets the server information as JSON with a GET request."""
    # Validate user made a GET request
    if request.method != 'GET':
        logger.warning('Invalid request method for server info request.')
        logger.debug(request)
        return HttpResponseBadRequest('Request must be GET request.')
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        logger.warning('User not authenticated for server info request.')
        logger.debug(request)
        return HttpResponseBadRequest('User not logged in. Login required.')

    # Log user access to server information
    logger.info('User downloaded server info: %s.' % request.user.username)
    ServerInfoAccessLog(user=request.user).save()

    # Form response
    try:
        # Get the latest published server info
        server_info_key = '/ServerInfo/latest'
        info = cache.get(server_info_key)
        if info is None:
            info = ServerInfo.objects.latest('timestamp')
            cache.set(server_info_key, info)
    except ServerInfo.DoesNotExist:
        # Failed to obtain server info
        return HttpResponseServerError('No server info available.')
    else:
        # Form JSON response
        data = {
            'server_info': info.json(),
            'server_time': str(datetime.datetime.now())
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
