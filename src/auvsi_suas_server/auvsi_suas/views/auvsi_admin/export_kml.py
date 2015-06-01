from auvsi_suas.models import UasTelemetry
from auvsi_suas.views import logger
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from simplekml import Kml
from simplekml import AltitudeMode
from simplekml import Color

__author__ = 'Joe'


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def generate_kml(_):
    """Evaluates the teams by forming a CSV containing useful stats."""
    logger.info('Admin downloaded team evaluation.')

    kml = Kml()
    users = User.objects.all()
    for user in users:
        # Ignore admins
        if user.is_superuser:
            continue
        uas_telemetry_logs = UasTelemetry.getAccessLogForUser(user)
        pts = []
        for entry in uas_telemetry_logs:
            pos = entry.uas_position.gps_position
            if pos.latitude == 0 and pos.longitude == 0:
                continue
            pts.append(
                (
                    pos.longitude,
                    pos.latitude,
                    entry.uas_position.altitude_msl,
                )
            )
        ls = kml.newlinestring(
            name=user.username,
            coords=pts,
            altitudemode=AltitudeMode.absolute,
        )
        ls.extrude = 1
        ls.style.linestyle.width = 2
        ls.style.linestyle.color = Color.blue

    response = HttpResponse(kml.kml())
    response['Content-Type'] = 'application/vnd.google-earth.kml+xml'
    response['Content-Disposition'] = 'attachment; filename=%s.kml' % 'mission'
    response['Content-Length'] = str(len(response.content))
    return response