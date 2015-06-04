"""Teams view."""
import json
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.views import logger
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest

# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def getTeams(request):
    """Gets a list of all teams."""
    # Only GET requests
    if request.method != 'GET':
        logger.warning('Invalid request method for teams request.')
        logger.debug(request)
        return HttpResponseBadRequest('Request must be GET request.')

    users = User.objects.all()
    teams = []

    for user in users:
        # Only standard users are exported
        if not user.is_superuser:
            teams.append({
                'name': user.username,
                'id': user.pk,
                'in_air':  TakeoffOrLandingEvent.userInAir(user),
                'active':  UasTelemetry.userActive(user),
            })

    return HttpResponse(json.dumps(teams),
                        content_type="application/json")
