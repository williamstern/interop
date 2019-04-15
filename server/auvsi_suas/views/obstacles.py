"""Interoperability obstacles view."""

import iso8601
import json
import logging
from auvsi_suas.proto import interop_api_pb2
from auvsi_suas.views.decorators import require_login
from auvsi_suas.views.missions import active_mission
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.generic import View
from google.protobuf import json_format

logger = logging.getLogger(__name__)


class Obstacles(View):
    """Gets the obstacle information as JSON with a GET request."""

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(Obstacles, self).dispatch(*args, **kwargs)

    def get(self, request):
        # Get active mission for forming responses.
        (mission, err) = active_mission()
        if err:
            return err

        # Form JSON response portion for stationary obstacles
        stationary_obstacles = mission.stationary_obstacles.select_related(
        ).all().order_by('pk')
        obst_set_proto = interop_api_pb2.ObstacleSet()
        for obst in stationary_obstacles:
            obst_proto = obst_set_proto.stationary_obstacles.add()
            obst_proto.latitude = obst.gps_position.latitude
            obst_proto.longitude = obst.gps_position.longitude
            obst_proto.radius = obst.cylinder_radius
            obst_proto.height = obst.cylinder_height

        # Return JSON data
        return HttpResponse(
            json_format.MessageToJson(obst_set_proto),
            content_type="application/json")
