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
from auvsi_suas.proto import interop_api_pb2
from auvsi_suas.views.decorators import require_login
from auvsi_suas.views.decorators import require_superuser
from auvsi_suas.views.json import ProtoJsonEncoder
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.generic import View
from google.protobuf import json_format

logger = logging.getLogger(__name__)


def mission_proto(mission):
    """Converts a mission to protobuf format."""
    mission_proto = interop_api_pb2.Mission()
    mission_proto.id = mission.pk

    for fly_zone in mission.fly_zones.select_related().all():
        fly_zone_proto = mission_proto.fly_zones.add()
        fly_zone_proto.altitude_min = fly_zone.altitude_msl_min
        fly_zone_proto.altitude_max = fly_zone.altitude_msl_max
        for boundary_point in fly_zone.boundary_pts.order_by(
                'order').select_related().all():
            boundary_proto = fly_zone_proto.boundary_points.add()
            boundary_proto.latitude = boundary_point.position.gps_position.latitude
            boundary_proto.longitude = boundary_point.position.gps_position.longitude

    for waypoint in mission.mission_waypoints.order_by(
            'order').select_related().all():
        waypoint_proto = mission_proto.waypoints.add()
        waypoint_proto.latitude = waypoint.position.gps_position.latitude
        waypoint_proto.longitude = waypoint.position.gps_position.longitude
        waypoint_proto.altitude = waypoint.position.altitude_msl

    for search_point in mission.search_grid_points.order_by(
            'order').select_related().all():
        search_point_proto = mission_proto.search_grid_points.add()
        search_point_proto.latitude = search_point.position.gps_position.latitude
        search_point_proto.longitude = search_point.position.gps_position.longitude

    mission_proto.off_axis_odlc_pos.latitude = mission.off_axis_odlc_pos.latitude
    mission_proto.off_axis_odlc_pos.longitude = mission.off_axis_odlc_pos.longitude

    mission_proto.emergent_last_known_pos.latitude = mission.emergent_last_known_pos.latitude
    mission_proto.emergent_last_known_pos.longitude = mission.emergent_last_known_pos.longitude

    mission_proto.air_drop_pos.latitude = mission.air_drop_pos.latitude
    mission_proto.air_drop_pos.longitude = mission.air_drop_pos.longitude

    stationary_obstacles = mission.stationary_obstacles.select_related().all(
    ).order_by('pk')
    for obst in stationary_obstacles:
        obst_proto = mission_proto.stationary_obstacles.add()
        obst_proto.latitude = obst.gps_position.latitude
        obst_proto.longitude = obst.gps_position.longitude
        obst_proto.radius = obst.cylinder_radius
        obst_proto.height = obst.cylinder_height

    return mission_proto


class Missions(View):
    """Handles requests for all missions for admins."""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(Missions, self).dispatch(*args, **kwargs)

    def get(self, request):
        missions = MissionConfig.objects.all()
        out = []
        for mission in missions:
            out.append(mission_proto(mission))

        return HttpResponse(
            json.dumps(out, cls=ProtoJsonEncoder),
            content_type="application/json")


class MissionsId(View):
    """Handles requests for a specific mission."""

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(MissionsId, self).dispatch(*args, **kwargs)

    def get(self, request, pk):
        try:
            mission = MissionConfig.objects.get(pk=pk)
        except MissionConfig.DoesNotExist:
            return HttpResponseNotFound('Mission %s not found.' % pk)

        return HttpResponse(
            json_format.MessageToJson(mission_proto(mission)),
            content_type="application/json")


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
        MissionConfig.kml_all(kml_mission, kml.document)

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

    def get(self, request, pk):
        try:
            mission = MissionConfig.objects.select_related().get(pk=pk)
        except MissionConfig.DoesNotExist:
            return HttpResponseBadRequest('Mission not found.')

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
