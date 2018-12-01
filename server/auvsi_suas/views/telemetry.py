"""Telemetry view."""

import iso8601
import json
import logging
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.uas_telemetry import UasTelemetry
from auvsi_suas.proto import interop_api_pb2
from auvsi_suas.views.decorators import require_login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.generic import View
from google.protobuf import json_format

logger = logging.getLogger(__name__)


class Telemetry(View):
    """GET/POST telemetry."""

    @method_decorator(require_login)
    def post(self, request):
        """Posts the UAS position with a POST request."""
        telemetry_proto = interop_api_pb2.Telemetry()
        try:
            json_format.Parse(request.body, telemetry_proto)
        except Exception as e:
            msg = 'Failed to parse request. Error: %s' % str(e)
            logger.warning(msg)
            logger.debug(request)
            return HttpResponseBadRequest(msg)

        if (not telemetry_proto.HasField('latitude') or
                not telemetry_proto.HasField('longitude') or
                not telemetry_proto.HasField('altitude') or
                not telemetry_proto.HasField('heading')):
            msg = 'Request missing fields.'
            logger.warning(msg)
            logger.debug(request)
            return HttpResponseBadRequest(
                'Failed to convert provided POST parameters to correct form.')
        else:
            # Check the values make sense
            if latitude < -90 or latitude > 90:
                logger.warning('User specified latitude out of valid range.')
                logger.debug(request)
                return HttpResponseBadRequest(
                    'Must provide latitude between -90 and 90 degrees.')
            if longitude < -180 or longitude > 180:
                logger.warning('User specified longitude out of valid range.')
                logger.debug(request)
                return HttpResponseBadRequest(
                    'Must provide longitude between -180 and 180 degrees.')
            if uas_heading < 0 or uas_heading > 360:
                logger.warning('User specified altitude out of valid range.')
                logger.debug(request)
                return HttpResponseBadRequest(
                    'Must provide heading between 0 and 360 degrees.')

            # Store telemetry
            logger.info('User uploaded telemetry: %s' % request.user.username)

            gpos = GpsPosition(latitude=latitude, longitude=longitude)
            gpos.save()

            apos = AerialPosition(gps_position=gpos, altitude_msl=altitude_msl)
            apos.save()

            telemetry = UasTelemetry(
                user=request.user, uas_position=apos, uas_heading=uas_heading)
            telemetry.save()

            return HttpResponse('UAS Telemetry Successfully Posted.')
