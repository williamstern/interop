from auvsi_suas.models import UasTelemetry
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from auvsi_suas.patches.simplekml_patch import Kml


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def generateKml(_):
    """ Generates a KML file HttpResponse"""

    kml = Kml(name='AUVSI SUAS Flight Data')
    kml_teams = kml.newfolder(name='Teams')
    kml_mission = kml.newfolder(name='Mission')
    users = User.objects.all()
    for user in users:
        # Ignore admins
        if user.is_superuser:
            continue
        UasTelemetry.kml(
            user=user,
            logs=UasTelemetry.getAccessLogForUser(user),
            kml=kml_teams,
        )

    response = HttpResponse(kml.kml())
    response['Content-Type'] = 'application/vnd.google-earth.kml+xml'
    response['Content-Disposition'] = 'attachment; filename=%s.kml' % 'mission'
    response['Content-Length'] = str(len(response.content))
    return response