"""Interoperability obstacles view."""

import iso8601
import json
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import ObstacleAccessLog
from auvsi_suas.models import StationaryObstacle
from auvsi_suas.views import boolean_param
from auvsi_suas.views import logger
from django.core.cache import cache
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils import timezone


def obstacles(request):
    """Gets the obstacle information as JSON with a GET request."""
    # Validate user made a GET request
    if request.method != 'GET':
        logger.warning('Invalid request method for obstacle info request.')
        logger.debug(request)
        return HttpResponseBadRequest('Request must be GET request.')
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        logger.warning('User not authenticated for obstacle info request.')
        logger.debug(request)
        return HttpResponseBadRequest('User not logged in. Login required.')

    log_access = True
    time = timezone.now()

    # ?log=(true|false) to enable/disable logging of superusers
    if 'log' in request.GET:
        if not request.user.is_superuser:
            return HttpResponseBadRequest(
                'Only superusers may set the log parameter')

        try:
            log_access = boolean_param(request.GET['log'])
        except ValueError as e:
            return HttpResponseBadRequest(e)

    # ?time=TIMESTAMP to get obstacle location at specific time
    if 'time' in request.GET:
        if not request.user.is_superuser:
            return HttpResponseBadRequest(
                'Only superusers may set the time parameter')

        try:
            time = iso8601.parse_date(request.GET['time'])
        except iso8601.ParseError:
            return HttpResponseBadRequest("Bad timestamp '%s'" % \
                                            request.GET['time'])

    # Log user access to obstacle info
    logger.info('User downloaded obstacle info: %s.' % request.user.username)
    if log_access:
        ObstacleAccessLog(user=request.user).save()

    # Form JSON response portion for stationary obstacles
    stationary_obstacles_cached = True
    stationary_obstacles_key = '/StationaryObstacle/all'
    stationary_obstacles = cache.get(stationary_obstacles_key)
    if stationary_obstacles is None:
        stationary_obstacles = StationaryObstacle.objects.all()
        stationary_obstacles_cached = False
    stationary_obstacles_json = []
    for cur_obst in stationary_obstacles:
        # Add current obstacle
        cur_obst_json = cur_obst.json()
        stationary_obstacles_json.append(cur_obst_json)

    # Form JSON response portion for moving obstacles
    moving_obstacles_cached = True
    moving_obstacles_key = '/MovingObstacle/all'
    moving_obstacles = cache.get(moving_obstacles_key)
    if moving_obstacles is None:
        moving_obstacles = MovingObstacle.objects.all()
        moving_obstacles_cached = False
    moving_obstacles_json = []
    for cur_obst in moving_obstacles:
        # Add current obstacle
        cur_obst_json = cur_obst.json(time=time)
        moving_obstacles_json.append(cur_obst_json)

    # Form final JSON response
    data = {
        'stationary_obstacles': stationary_obstacles_json,
        'moving_obstacles': moving_obstacles_json
    }

    # Cache obstacles for next request
    if not stationary_obstacles_cached:
        cache.set(stationary_obstacles_key, stationary_obstacles)
    if not moving_obstacles_cached:
        cache.set(moving_obstacles_key, moving_obstacles)

    # Return JSON data
    return HttpResponse(json.dumps(data), content_type="application/json")
