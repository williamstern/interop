"""Missions view."""

import copy
import csv
import io
import json
import logging
import zipfile
from auvsi_suas.models import mission_evaluation
from auvsi_suas.models.fly_zone import FlyZone
from auvsi_suas.models.mission_config import MissionConfig
from auvsi_suas.models.uas_telemetry import UasTelemetry
from auvsi_suas.patches.simplekml_patch import Kml
from auvsi_suas.patches.simplekml_patch import RefreshMode
from auvsi_suas.views.decorators import require_login
from auvsi_suas.views.decorators import require_superuser
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from google.protobuf import json_format

logger = logging.getLogger(__name__)


def active_mission():
    """Gets the single active mission.

    Returns:
        (MissionConfig, HttpResponse). The MissionConfig is the single active
        mission, or None if there is an error. HttpResponse is None if a config
        could be obtained, or the error message if not.
    """
    missions = MissionConfig.objects.filter(is_active=True)
    if len(missions) != 1:
        logger.warning('Invalid number of active missions. Missions: %s.',
                       str(missions))
        return (None,
                HttpResponseServerError('Invalid number of active missions.'))

    return (missions[0], None)


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


class Missions(View):
    """Handles requests for all missions."""

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(Missions, self).dispatch(*args, **kwargs)

    def get(self, request):
        missions = MissionConfig.objects.all()
        out = []
        for mission in missions:
            out.append(mission.json(request.user.is_superuser))

        # Older versions of JS allow hijacking the Array constructor to steal
        # JSON data. It is not a problem in recent versions.
        return JsonResponse(out, safe=False)


class MissionsId(View):
    """Handles requests for a specific mission."""

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(MissionsId, self).dispatch(*args, **kwargs)

    def get(self, request, pk):
        try:
            mission = MissionConfig.objects.get(pk=pk)
            return JsonResponse(mission.json(request.user.is_superuser))
        except MissionConfig.DoesNotExist:
            return HttpResponseNotFound('Mission %s not found.' % pk)


class ExportKml(View):
    """ Generates a KML file HttpResponse"""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(ExportKml, self).dispatch(*args, **kwargs)

    def get(self, request):
        kml = Kml(name='AUVSI SUAS Flight Data')
        kml_teams = kml.newfolder(name='Teams')
        kml_mission = kml.newfolder(name='Missions')
        users = User.objects.all()
        for user in users:
            # Ignore admins
            if user.is_superuser:
                continue
            UasTelemetry.kml(
                user=user,
                logs=UasTelemetry.by_user(user),
                kml=kml_teams,
                kml_doc=kml.document)
        MissionConfig.kml_all(kml_mission, kml.document)
        kml_flyzone = kml.newfolder(name='Fly Zones')
        FlyZone.kml_all(kml_flyzone)

        response = HttpResponse(kml.kml())
        response['Content-Type'] = 'application/vnd.google-earth.kml+xml'
        response['Content-Disposition'] = 'attachment; filename=mission.kml'
        response['Content-Length'] = str(len(response.content))
        return response


class LiveKml(View):
    """ Generates a KML for live display.
    This KML uses a network link to update via the update.kml endpoint
    """

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(LiveKml, self).dispatch(*args, **kwargs)

    def get(self, request):
        kml = Kml(name='AUVSI SUAS LIVE Flight Data')
        kml_mission = kml.newfolder(name='Missions')

        (mission, err) = active_mission()
        if err:
            return err
        MissionConfig.kml_all(kml_mission, kml.document, [mission])

        kml_flyzone = kml.newfolder(name='Fly Zones')
        FlyZone.kml_all(kml_flyzone)

        parameters = '?sessionid={}'.format(request.COOKIES['sessionid'])
        uri = request.build_absolute_uri(
            '/api/missions/update.kml') + parameters

        netlink = kml.newnetworklink(name="Live Data")
        netlink.link.href = uri
        netlink.link.refreshmode = RefreshMode.oninterval
        netlink.link.refreshinterval = 1.0

        response = HttpResponse(kml.kml())
        response['Content-Type'] = 'application/vnd.google-earth.kml+xml'
        response['Content-Disposition'] = 'attachment; filename=live.kml'
        response['Content-Length'] = str(len(response.content))
        return response


def set_request_session_from_cookie(func):
    def wrapper(request):
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
            return func(request)

    return wrapper


class LiveKmlUpdate(View):
    """Generates the live update portion of LiveKml"""

    @method_decorator(set_request_session_from_cookie)
    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(LiveKmlUpdate, self).dispatch(*args, **kwargs)

    def get(self, request):
        kml = Kml(name='LIVE Data')
        UasTelemetry.live_kml(kml, timedelta(seconds=5))

        response = HttpResponse(kml.kml())
        response['Content-Type'] = 'application/vnd.google-earth.kml+xml'
        response['Content-Disposition'] = 'attachment; filename=update.kml'
        response['Content-Length'] = str(len(response.content))
        return response


class Evaluate(View):
    """Evaluates the teams and returns a zip file with CSV & JSON data.

    Zip file contains a master CSV and JSON file with all evaluation data.
    It also contains per-team JSON files for individual team feedback.
    """

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(Evaluate, self).dispatch(*args, **kwargs)

    def pretty_json(self, json_str):
        """Generates a pretty-print json from any json."""
        return json.dumps(json.loads(json_str), indent=4)

    def csv_from_json(self, json_list):
        """Generates a CSV string from a list of rows as JSON strings."""
        csv_list = []
        for json_row in json_list:
            csv_dict = {}
            work_queue = [([], json.loads(json_row))]
            while len(work_queue) > 0:
                (cur_prefixes, cur_val) = work_queue.pop()
                if isinstance(cur_val, dict):
                    for (key, val) in cur_val.items():
                        new_prefixes = copy.copy(cur_prefixes)
                        new_prefixes.append(str(key))
                        work_queue.append((new_prefixes, val))
                elif isinstance(cur_val, list):
                    for ix, val in enumerate(cur_val):
                        new_prefixes = copy.copy(cur_prefixes)
                        new_prefixes.append(str(ix))
                        work_queue.append((new_prefixes, val))
                else:
                    column_key = '.'.join(cur_prefixes)
                    csv_dict[column_key] = cur_val
            csv_list.append(csv_dict)

        col_headers = set()
        for csv_dict in csv_list:
            col_headers.update(csv_dict.keys())
        col_headers = sorted(col_headers)

        csv_io = io.StringIO()
        writer = csv.DictWriter(csv_io, fieldnames=col_headers)
        writer.writeheader()
        for csv_dict in csv_list:
            writer.writerow(csv_dict)
        csv_output = csv_io.getvalue()
        csv_io.close()

        return csv_output

    def get(self, request):
        logger.info('Admin downloading team evaluation.')

        # Get the mission to evaluate a team for.
        mission, error = mission_for_request(request.GET)
        if error:
            logger.warning('Could not get mission to evaluate teams.')
            return error

        # Get the optional team to eval.
        users = None
        if 'team' in request.GET:
            try:
                team = int(request.GET['team'])
                users = [User.objects.get(pk=team)]
            except TypeError:
                return HttpResponseBadRequest('Team not an ID.')
            except User.DoesNotExist:
                return HttpResponseNotFound('Team not found.')

        # Get the eval data for the teams.
        mission_eval = mission_evaluation.evaluate_teams(mission, users)
        if not mission_eval:
            logger.warning('No data for team evaluation.')
            return HttpResponseServerError(
                'Could not get user evaluation data.')

        # Form Zip file.
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, 'w') as zip_file:
            zip_file.writestr(
                '/evaluate_teams/all.json',
                self.pretty_json(json_format.MessageToJson(mission_eval)))
            team_jsons = []
            for team_eval in mission_eval.teams:
                team_json = self.pretty_json(
                    json_format.MessageToJson(team_eval))
                zip_file.writestr(
                    '/evaluate_teams/teams/%s.json' % team_eval.team,
                    team_json)
                team_jsons.append(team_json)

            zip_file.writestr('/evaluate_teams/all.csv',
                              self.csv_from_json(team_jsons))
        zip_output = zip_io.getvalue()
        zip_io.close()

        return HttpResponse(zip_output, content_type='application/zip')
