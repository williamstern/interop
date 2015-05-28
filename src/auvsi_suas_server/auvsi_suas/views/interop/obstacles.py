"""Interoperability obstacles view."""

import json
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import ObstacleAccessLog
from auvsi_suas.models import StationaryObstacle
from auvsi_suas.views import logger
from django.core.cache import cache
from django.http import HttpResponse
from django.http import HttpResponseBadRequest


def getObstacles(request):
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

    # Log user access to obstacle info
    logger.info('User downloaded obstacle info: %s.' % request.user.username)
    ObstacleAccessLog(user=request.user).save()

    # Form JSON response portion for stationary obstacles
    stationary_obstacles_cached = True
    stationary_obstacles_key = '/StationaryObstacle/all'
    stationary_obstacles = cache.get(stationary_obstacles_key)
    if stationary_obstacles is None:
        stationary_obstacles = StationaryObstacle.objects.all()
        stationary_obstacles_cached = False
    stationary_obstacles_json = list()
    for cur_obst in stationary_obstacles:
        # Add current obstacle
        cur_obst_json = cur_obst.toJSON()
        stationary_obstacles_json.append(cur_obst_json)

    # Form JSON response portion for moving obstacles
    moving_obstacles_cached = True
    moving_obstacles_key = '/MovingObstacle/all'
    moving_obstacles = cache.get(moving_obstacles_key)
    if moving_obstacles is None:
        moving_obstacles = MovingObstacle.objects.all()
        moving_obstacles_cached = False
    moving_obstacles_json = list()
    for cur_obst in moving_obstacles:
        # Add current obstacle
        cur_obst_json = cur_obst.toJSON()
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
    return HttpResponse(json.dumps(data),
                        content_type="application/json")


