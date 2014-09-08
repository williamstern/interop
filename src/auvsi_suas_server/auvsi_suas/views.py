from auvsi_suas.models import ServoInfo
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render


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
    """Gets the server information with a GET request."""
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')
    # Validate user made a GET request
    if request.method != 'GET':
        return HttpResponseBadRequest('Servo info request must be GET request.')

    # Get the latest published servo info
    server_info = ServoInfo.objects.latest('timestamp') 
    if not servo_info:
        return HttpResponseServerError('No server information available.')

    # Form JSON response
    data = dict()
    data['time'] = int(time.time() * 1000)
    data['message'] = servo_info.team_msg
    data['message_timestamp'] = servo_info.timestamp
    return JsonResponse(data)


def getObstacles(request):
    """Gets the obstacle information with a GET request."""
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')

    # TODO


def updateUasPosition(request):
    """Posts the UAS position with a POST request containing JSON data."""
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')

    # TODO


# login_required()
# @user_passes_test(lambda u: u.is_superuser)
