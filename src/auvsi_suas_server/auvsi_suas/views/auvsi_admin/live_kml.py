from auvsi_suas.models import FlyZone
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import UasTelemetry
from auvsi_suas.patches.simplekml_patch import Kml
from auvsi_suas.patches.simplekml_patch import RefreshMode
from datetime import timedelta
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def generateKml(_):
    """ Generates a KML file HttpResponse"""
    kml = Kml(name='AUVSI SUAS LIVE Flight Data')
    kml_mission = kml.newfolder(name='Missions')
    MissionConfig.kml_all(kml_mission)
    kml_flyzone = kml.newfolder(name='Fly Zones')
    FlyZone.kml_all(kml_flyzone)

    netlink = kml.newnetworklink(name="Live Data")
    netlink.link.href = 'http://localhost:8080/auvsi_admin/update.kml'
    netlink.link.refreshmode = RefreshMode.oninterval
    netlink.link.refreshinterval = 0.5

    response = HttpResponse(kml.kml())
    response['Content-Type'] = 'application/vnd.google-earth.kml+xml'
    response['Content-Disposition'] = 'attachment; filename=%s.kml' % 'live'
    response['Content-Length'] = str(len(response.content))
    return response


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