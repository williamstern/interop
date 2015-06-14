from auvsi_suas.models import FlyZone
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import UasTelemetry
from auvsi_suas.patches.simplekml_patch import Kml
from auvsi_suas.patches.simplekml_patch import RefreshMode
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseForbidden


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def generateKml(request):
    """ Generates a KML file HttpResponse"""
    kml = Kml(name='AUVSI SUAS LIVE Flight Data')
    kml_mission = kml.newfolder(name='Missions')
    MissionConfig.kml_all(kml_mission)
    kml_flyzone = kml.newfolder(name='Fly Zones')
    FlyZone.kml_all(kml_flyzone)

    parameters = '?sessionid={}'.format(request.COOKIES['sessionid'])
    uri = request.build_absolute_uri('/auvsi_admin/update.kml')+parameters

    netlink = kml.newnetworklink(name="Live Data")
    netlink.link.href = uri
    netlink.link.refreshmode = RefreshMode.oninterval
    netlink.link.refreshinterval = 0.5

    response = HttpResponse(kml.kml())
    response['Content-Type'] = 'application/vnd.google-earth.kml+xml'
    response['Content-Disposition'] = 'attachment; filename=%s.kml' % 'live'
    response['Content-Length'] = str(len(response.content))
    return response


def cookiePacker(request):
    # Check if a sessionid has been provided
    if 'sessionid' not in request.GET:
            return HttpResponseForbidden()

    try:
        # pack the params back into the cookie
        request.COOKIES['sessionid'] = request.GET['sessionid']

        # Update the user associated with the cookie
        session = Session.objects.get(session_key=request.GET['sessionid'])
        uid = session.get_decoded().get('_auth_user_id')
        request.user = User.objects.get(pk=uid)
    except ObjectDoesNotExist:
        return HttpResponseForbidden()
    else:
        return generateLiveKml(request)


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def generateLiveKml(_):
    """ Generates a KML file HttpResponse"""
    kml = Kml(name='LIVE Data')
    MovingObstacle.live_kml(kml, timedelta(seconds=5))
    UasTelemetry.live_kml(kml, timedelta(seconds=5))

    response = HttpResponse(kml.kml())
    response['Content-Type'] = 'application/vnd.google-earth.kml+xml'
    response['Content-Disposition'] = 'attachment; filename=%s.kml' % 'update'
    response['Content-Length'] = str(len(response.content))
    return response