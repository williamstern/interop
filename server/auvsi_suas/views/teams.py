"""Teams view."""

import json
import logging
from auvsi_suas.models.takeoff_or_landing_event import TakeoffOrLandingEvent
from auvsi_suas.models.uas_telemetry import UasTelemetry
from auvsi_suas.proto import interop_admin_api_pb2
from auvsi_suas.views.decorators import require_superuser
from auvsi_suas.views.missions import active_mission
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.generic import View
from google.protobuf import json_format

logger = logging.getLogger(__name__)


def user_json(user):
    """Generate JSON string for user."""
    team_status_proto = interop_admin_api_pb2.TeamStatus()
    team_status_proto.team = user.username
    team_status_proto.in_air = TakeoffOrLandingEvent.user_in_air(user)

    telemetry = UasTelemetry.last_for_user(user)
    if telemetry is not None:
        apos = telemetry.uas_position
        gpos = apos.gps_position
        telemetry_proto = team_status_proto.telemetry
        telemetry_proto.latitude = gpos.latitude
        telemetry_proto.longitude = gpos.longitude
        telemetry_proto.altitude = apos.altitude_msl
        telemetry_proto.heading = telemetry.uas_heading
        team_status_proto.telemetry_timestamp = telemetry.timestamp.isoformat()

    return json_format.MessageToJson(team_status_proto)


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
                teams.append(json.loads(user_json(user)))

        return HttpResponse(json.dumps(teams), content_type="application/json")


class Team(View):
    """GET/PUT specific team."""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(Team, self).dispatch(*args, **kwargs)

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseBadRequest('Unknown team %s' % username)

        return HttpResponse(user_json(user), content_type="application/json")
