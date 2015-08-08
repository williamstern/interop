"""Missions view."""
import json
from auvsi_suas.models import MissionConfig
from auvsi_suas.views import logger
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def missions(request):
    """Gets a list of all missions."""
    # Only GET requests
    if request.method != 'GET':
        logger.warning('Invalid request method for missions request.')
        logger.debug(request)
        return HttpResponseBadRequest('Request must be GET request.')

    missions = MissionConfig.objects.all()
    out = []

    for mission in missions:
        out.append(mission.json())

    return HttpResponse(json.dumps(out), content_type="application/json")
