"""Teams view."""
import json
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.views import logger
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest


def user_json(user):
    """Generate JSON-style dict for user."""
    return {
        'name': user.username,
        'id': user.pk,
        'in_air': TakeoffOrLandingEvent.user_in_air(user),
        'active': UasTelemetry.user_active(user),
    }


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def teams(request):
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
            teams.append(user_json(user))

    return HttpResponse(json.dumps(teams), content_type="application/json")


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def teams_id(request, pk):
    """GET/PUT specific team."""
    # Only GET/PUT requests
    if request.method not in ['GET', 'PUT']:
        logger.warning('Invalid request method for teams request.')
        logger.debug(request)
        return HttpResponseBadRequest('Request must be GET or PUT request.')

    try:
        user = User.objects.get(pk=int(pk))
    except User.DoesNotExist:
        return HttpResponseBadRequest('Unknown team %s' % pk)

    # PUT allows updating in-air status
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON: %s' % request.body)

        # We ignore everything except 'in_air'
        if 'in_air' in data:
            in_air = data['in_air']

            if in_air is not True and in_air is not False:
                return HttpResponseBadRequest('in_air must be boolean')

            currently_in_air = TakeoffOrLandingEvent.user_in_air(user)

            # New event only necessary if changing status
            if currently_in_air != in_air:
                event = TakeoffOrLandingEvent(user=user, uas_in_air=in_air)
                event.save()

    return HttpResponse(json.dumps(user_json(user)),
                        content_type="application/json")
