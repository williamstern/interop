"""Views which users interact with in AUVSI SUAS System."""

import datetime
import json
import time
import numpy as np
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from auvsi_suas.models import UasTelemetry
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.shortcuts import render
from scipy import interpolate


def index(request):
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
        return HttpResponseBadRequest('Login request must be POST request.')

    # Attempt authentication
    try:
        # Obtain username and password from POST parameters
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        # Failed to get POST parameters, invalid request
        return HttpResponseBadRequest('Login must be POST request with '
                '"username" and "password" parameters.')
    else:
        # Use credentials to authenticate
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Successful authentication with active user, login
            login(request, user)
            return HttpResponse('Login Successful.')
        else:
            # Invalid user credentials, invalid request
            return HttpResponseBadRequest('Invalid Credentials.')


def getServerInfo(request):
    """Gets the server information as JSON with a GET request."""
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')
    # Validate user made a GET request
    if request.method != 'GET':
        return HttpResponseBadRequest('Request must be GET request.')

    # Log user access to server information
    access_log = ServerInfoAccessLog()
    access_log.user = request.user
    access_log.save()

    # Form response
    try:
        # Get the latest published server info
        server_info = ServerInfo.objects.latest('timestamp')
    except ServerInfo.DoesNotExist:
        # Failed to obtain server info
        return HttpResponseServerError('No server info available.')
    else:
        # Form JSON response
        data = dict()
        data['server_time'] = str(datetime.datetime.now())
        data['message'] = server_info.team_msg
        data['message_timestamp'] = str(server_info.timestamp)
        return HttpResponse(json.dumps(data),
                            content_type="application/json")


def getObstacles(request):
    """Gets the obstacle information as JSON with a GET request."""
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')
    # Validate user made a GET request
    if request.method != 'GET':
        return HttpResponseBadRequest('Request must be GET request.')

    # Form JSON response portion for stationary obstacles
    stationary_obstacles = StationaryObstacles.objects.all()
    stationary_obstacles_json = list()
    for cur_obst in stationary_obstacles:
        cur_obst_json = dict()
        cur_gps = dict()
        # Set obstacle position
        cur_gps['latitude'] = cur_obst.gps_position.latitude
        cur_gps['longitude'] = cur_obst.gps_position.longitude
        cur_obst_json['gps_position'] = cur_gps
        # Set obstacle size
        cur_obst_json['cylinder_radius'] = cur_obst.cylinder_radius
        cur_obst_json['cylinder_height'] = cur_obst.cylinder_height
        # Add current obstacle
        stationary_obstacles_json.append(cur_obst_json)

    # Form JSON response portion for moving obstacles
    moving_obstacles = MovingObstacle.objects.all()
    moving_obstacles_json = list()
    for cur_obst in moving_obstacles:
        cur_obst_json = dict()
        # Set obstacle size
        cur_obst_json['sphere_radius'] = cur_obst.sphere_radius
        # Get obstacle speed
        speed_max = cur_obst.speed_max
        if speed_max <= 0:
            continue
        # Obtain waypoint positions which define flight path
        waypoints = cur_obst.waypoints.order_by('order')
        num_waypoints = len(waypoints)
        positions = np.zeros(num_waypoints + 1, 3)
        for waypoint_id in range(num_waypoints):
            cur_waypoint = waypoints[waypoint_id]
            cur_position = cur_waypoint.position
            cur_gps_pos = cur_position.gps_position
            positions[waypoint_id, 0] = cur_gps_pos.latitude
            positions[waypoint_id, 1] = cur_gps_pos.longitude
            positions[waypoint_id, 2] = cur_position.msl_altitude
        # Compute times of waypoint positions
        pos_times = np.zeros(num_waypoints + 1)
        for waypoint_id in range(1, num_waypoints):
            waypoint_t = waypoints[waypoint_id]
            waypoint_tm1 = waypoints[waypoint_id-1]
            waypoint_dist = waypoint_tm1.distanceTo(waypoint_t)
            waypoint_travel_time = waypoint_dist / speed_max
            cur_time = pos_times[waypoint_id-1] + waypoint_travel_time
            pos_times[waypoint_id] = cur_time
        first_point = waypoints[0]
        final_point = waypoints[num_waypoints-1]
        final_dist = final_point.distanceTo(first_point)
        final_travel_time = final_dist / speed_max
        final_time = pos_times[num_waypoints-1] + final_travel_time
        pos_times[num_waypoints] = final_time
        # Use spline interpolation to find current position
        tck = interpolate.splrep(pos_times, positions, per=1)
        cur_time = np.mod(time.time(), pos_times[num_waypoints])
        cur_pos = interpolate.splev(cur_time, tck)
        cur_obst_json['latitude'] = cur_pos[0]
        cur_obst_json['longitude'] = cur_pos[1]
        cur_obst_json['altitude_msl'] = cur_pos[2]
        # Add current obstacle
        moving_obstacles_json.append(cur_obst_json)

    # Form final JSON response
    data = dict()
    data['stationary_obstacles'] = stationary_obstacles_json
    data['moving_obstacles'] = moving_obstacles_json
    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def postUasPosition(request):
    """Posts the UAS position with a POST request.

    User must send a POST request with the following paramters:
    latitude: A latitude in decimal degrees.
    longitude: A logitude in decimal degrees.
    msl_altitude: An MSL altitude in decimal feet.
    uas_heading: The UAS heading in decimal degrees. (0=north, 90=east)
    """
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')
    # Validate user made a POST request
    if request.method != 'POST':
        return HttpResponseBadRequest('Request must be POST request.')

    try:
        # Get the parameters
        latitude = float(request.POST['latitude'])
        longitude = float(request.POST['longitude'])
        msl_altitude = float(request.POST['msl_altitude'])
        uas_heading = float(request.POST['uas_heading'])
    except KeyError:
        # Failed to get POST parameters
        return HttpResponseBadRequest(
                'Posting UAS position must contain POST parameters "latitude", '
                '"longitude", "msl_altitude", and "uas_heading".')
    except ValueError:
        # Failed to convert parameters
        return HttpResponseBadRequest(
                'Failed to convert provided POST parameters to correct form.')
    else:
        # Check the values make sense
        if latitude < -90 or latitude > 90:
            return HttpResponseBadRequest(
                    'Must provide latitude between -90 and 90 degrees.')
        if longitude < -180 or longitude > 180:
            return HttpResponseBadRequest(
                    'Must provide longitude between -180 and 180 degrees.')
        if uas_heading < 0 or uas_heading > 360:
            return HttpResponseBadRequest(
                    'Must provide heading between 0 and 360 degrees.')

        # Store telemetry
        gps_position = GpsPosition()
        gps_position.latitude = latitude
        gps_position.longitude = longitude
        gps_position.save()
        aerial_position = AerialPosition()
        aerial_position.gps_position = gps_position
        aerial_position.msl_altitude = msl_altitude
        aerial_position.save()
        uas_telemetry = UasTelemetry()
        uas_telemetry.user = request.user
        uas_telemetry.uas_position = aerial_position
        uas_telemetry.uas_heading = uas_heading
        uas_telemetry.save()

        return HttpResponse('UAS Telemetry Successfully Posted.')


# login_required()
# @user_passes_test(lambda u: u.is_superuser)
