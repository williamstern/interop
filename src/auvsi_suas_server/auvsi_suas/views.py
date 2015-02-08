"""Views which users interact with in AUVSI SUAS System."""

import copy
import cStringIO
import csv
import datetime
import json
import logging
import time
import numpy as np
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import FlyZone
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import ObstacleAccessLog
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from auvsi_suas.models import StationaryObstacle
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import Waypoint
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.shortcuts import render
from scipy import interpolate


# Logging for the module
logger = logging.getLogger(__name__)


def indexView(request):
    """Main view for users connecting via web browsers.

    This view downloads and displays a JS view. This view first logs in the
    user. If the user is a superuser, it shows the Judging view which is used
    to manage the competition and evaluate teams.
    """
    return render(request, 'auvsi_suas/index.html')


def loginUser(request):
    """Logs the user in with a POST request using the given parameters.

    This view performs the login process for the user. The POST paramters must
    include 'username' and 'password'. Users can programatically send a login
    request to this view which will return a cookie containing the session ID.
    Users then send this cookie with each request to make requests as an
    authenticated user.
    """
    # Validate user made a POST request
    if request.method != 'POST':
        logger.warning('Invalid request method for login attempt.')
        return HttpResponseBadRequest('Login request must be POST request.')

    # Attempt authentication
    try:
        # Obtain username and password from POST parameters
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        # Failed to get POST parameters, invalid request
        logger.warning('Did not specify username & password in login request.')
        return HttpResponseBadRequest('Login must be POST request with '
                '"username" and "password" parameters.')
    else:
        # Use credentials to authenticate
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Successful authentication with active user, login
            login(request, user)
            logger.info('User logged in: %s.' % user.username)
            return HttpResponse('Login Successful.')
        else:
            # Invalid user credentials, invalid request
            logger.warning('Invalid credentials in login request.')
            logger.debug(request)
            return HttpResponseBadRequest('Invalid Credentials.')


def getServerInfo(request):
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
    access_log = ServerInfoAccessLog()
    access_log.user = request.user
    access_log.save()

    # Form response
    try:
        # Get the latest published server info
        server_info_key = '/ServerInfo/latest'
        server_info = cache.get(server_info_key)
        if server_info is None:
            server_info = ServerInfo.objects.latest('timestamp')
            cache.set(server_info_key, server_info)
    except ServerInfo.DoesNotExist:
        # Failed to obtain server info
        return HttpResponseServerError('No server info available.')
    else:
        # Form JSON response
        data = {
            'server_info': server_info.toJSON(),
            'server_time': str(datetime.datetime.now())
        }
        return HttpResponse(json.dumps(data),
                            content_type="application/json")


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
    access_log = ObstacleAccessLog()
    access_log.user = request.user
    access_log.save()

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


def postUasPosition(request):
    """Posts the UAS position with a POST request.

    User must send a POST request with the following paramters:
    latitude: A latitude in decimal degrees.
    longitude: A logitude in decimal degrees.
    altitude_msl: An MSL altitude in decimal feet.
    uas_heading: The UAS heading in decimal degrees. (0=north, 90=east)
    """
    # Validate user made a POST request
    if request.method != 'POST':
        logger.warning('Invalid request method for uas telemetry request.')
        logger.debug(request)
        return HttpResponseBadRequest('Request must be POST request.')
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        logger.warning('User not authenticated for uas telemetry request.')
        logger.debug(request)
        return HttpResponseBadRequest('User not logged in. Login required.')

    try:
        # Get the parameters
        latitude = float(request.POST['latitude'])
        longitude = float(request.POST['longitude'])
        altitude_msl = float(request.POST['altitude_msl'])
        uas_heading = float(request.POST['uas_heading'])
    except KeyError:
        # Failed to get POST parameters
        logger.warning(
                'User did not specify all params for uas telemetry request.')
        logger.debug(request)
        return HttpResponseBadRequest(
                'Posting UAS position must contain POST parameters "latitude", '
                '"longitude", "altitude_msl", and "uas_heading".')
    except ValueError:
        # Failed to convert parameters
        logger.warning(
                'User specified a param which could not converted to an ' + 
                'appropriate type.')
        logger.debug(request)
        return HttpResponseBadRequest(
                'Failed to convert provided POST parameters to correct form.')
    else:
        # Check the values make sense
        if latitude < -90 or latitude > 90:
            logger.warning('User specified latitude out of valid range.')
            logger.debug(request)
            return HttpResponseBadRequest(
                    'Must provide latitude between -90 and 90 degrees.')
        if longitude < -180 or longitude > 180:
            logger.warning('User specified longitude out of valid range.')
            logger.debug(request)
            return HttpResponseBadRequest(
                    'Must provide longitude between -180 and 180 degrees.')
        if uas_heading < 0 or uas_heading > 360:
            logger.warning('User specified altitude out of valid range.')
            logger.debug(request)
            return HttpResponseBadRequest(
                    'Must provide heading between 0 and 360 degrees.')

        # Store telemetry
        logging.info('User uploaded telemetry: %s' % request.user.username)
        gps_position = GpsPosition()
        gps_position.latitude = latitude
        gps_position.longitude = longitude
        gps_position.save()
        aerial_position = AerialPosition()
        aerial_position.gps_position = gps_position
        aerial_position.altitude_msl = altitude_msl
        aerial_position.save()
        uas_telemetry = UasTelemetry()
        uas_telemetry.user = request.user
        uas_telemetry.uas_position = aerial_position
        uas_telemetry.uas_heading = uas_heading
        uas_telemetry.save()

        return HttpResponse('UAS Telemetry Successfully Posted.')


@user_passes_test(lambda u: u.is_superuser)
def evaluateTeams(request):
    """Evaluates the teams by forming a CSV containing useful stats."""
    logger.info('Admin downloaded team evaluation.')
    # Require admin access
    # Get the mission for evaluation
    missions = MissionConfig.objects.all()
    if not missions or not missions[0]:
        logger.error('No mission defined for which to evaluate teams.')
        return HttpResponseServerError('No mission defined.')
    mission = missions[0]
    # Get the eval data for the teams
    user_eval_data = mission.evaluateTeams()
    if not user_eval_data:
        logger.warning('No data for team evaluation.')
        return HttpResponseServerError('Could not get user evaluation data.')
    # Reformat to column oriented
    user_col_data = dict()
    for (user, eval_data) in user_eval_data.iteritems():
        col_data = user_col_data.setdefault(user, dict())
        col_data['username'] = user.username
        work_queue = [([], eval_data)]
        while len(work_queue) > 0:
            (cur_prefixes, cur_map) = work_queue.pop()
            for (key, val) in cur_map.iteritems():
                new_prefixes = copy.copy(cur_prefixes)
                new_prefixes.append(str(key))
                if isinstance(val, dict):
                    work_queue.append((new_prefixes, val))
                else:
                    column_key = '.'.join(new_prefixes)
                    col_data[column_key] = val
    # Get column headers
    col_headers = set()
    for col_data in user_col_data.values():
        for header in col_data.keys():
            col_headers.add(header)
    col_headers = sorted(col_headers)
    # Write output
    csv_output = cStringIO.StringIO()
    writer = csv.DictWriter(csv_output, fieldnames=col_headers)
    writer.writeheader()
    for col_data in user_col_data.values():
        writer.writerow(col_data)
    output = csv_output.getvalue()
    csv_output.close()
    return HttpResponse(output)


# @login_required()
# @user_passes_test(lambda u: u.is_superuser)
