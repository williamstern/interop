"""Teams view."""

import json
import logging
from auvsi_suas.models.takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.models.uas_telemetry import UasTelemetry
from auvsi_suas.views.decorators import require_superuser
from auvsi_suas.views.missions import active_mission
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.generic import View

logger = logging.getLogger(__name__)


def user_json(user):
    """Generate JSON-style dict for user."""
    telemetry = UasTelemetry.last_for_user(user)
    return {
        'name': user.username,
        'id': user.pk,
        'in_air': TakeoffOrLandingEvent.user_in_air(user),
        'telemetry': telemetry.json() if telemetry else None
    }


class Teams(View):
    """Gets a list of all teams."""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(Teams, self).dispatch(*args, **kwargs)

    def get(self, request):
        users = User.objects.all()
        teams = []

        for user in users:
            # Only standard users are exported
            if not user.is_superuser:
                teams.append(user_json(user))

        return HttpResponse(json.dumps(teams), content_type="application/json")


class TeamsId(View):
    """GET/PUT specific team."""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(TeamsId, self).dispatch(*args, **kwargs)

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=int(pk))
        except User.DoesNotExist:
            return HttpResponseBadRequest('Unknown team %s' % pk)

        return HttpResponse(
            json.dumps(user_json(user)), content_type="application/json")

    def put(self, request, pk):
        """PUT allows updating status."""
        try:
            user = User.objects.get(pk=int(pk))
        except User.DoesNotExist:
            return HttpResponseBadRequest('Unknown team %s' % pk)
        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON: %s' % request.body)

        # Potential events to update.
        takeoff_event = None
        clock_event = None
        # Update whether UAS is in air.
        if 'in_air' in data:
            in_air = data['in_air']
            if not isinstance(in_air, bool):
                return HttpResponseBadRequest('in_air must be boolean')

            currently_in_air = TakeoffOrLandingEvent.user_in_air(user)
            # New event only necessary if changing status
            if currently_in_air != in_air:
                takeoff_event = TakeoffOrLandingEvent(
                    user=user, uas_in_air=in_air)
        # Request was valid. Save updates.
        if takeoff_event:
            takeoff_event.save()
        if clock_event:
            clock_event.save()

        return HttpResponse(
            json.dumps(user_json(user)), content_type="application/json")


def mission_for_request(request_params):
    """Gets the mission for the request.

    Args:
        request_params: The request parameter dict. If this has a 'mission'
            parameter, it will get the corresponding mission.
    Returns:
        Returns (MissionConfig, HttpResponse). The MissionConfig is
        the one corresponding to the request parameter, or the single active
        MissionConfig if one exists. The HttpResponse is the appropriate error
        if a MissionConfig could not be obtained.
    """
    # If specific mission requested, get it.
    if 'mission' in request_params:
        try:
            mission_id_str = request_params['mission']
            mission_id = int(mission_id_str)
            mission = MissionConfig.objects.get(pk=mission_id)
            return (mission, None)
        except ValueError:
            logger.warning('Invalid mission ID given. ID: %d.', mission_id_str)
            return (None,
                    HttpResponseBadRequest('Mission ID is not an integer.'))
        except MissionConfig.DoesNotExist:
            logger.warning('Given mission ID not found. ID: %d.', mission_id)
            return (None, HttpResponseBadRequest('Mission not found.'))

    # Mission not specified, get the single active mission.
    return active_mission()
