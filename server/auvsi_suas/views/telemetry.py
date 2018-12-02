"""Telemetry view."""

import iso8601
import json
import logging
from auvsi_suas.models.aerial_position import AerialPosition
from auvsi_suas.models.gps_position import GpsPosition
from auvsi_suas.models.uas_telemetry import UasTelemetry
from auvsi_suas.views.decorators import require_login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.generic import View

logger = logging.getLogger(__name__)


class Telemetry(View):
    """GET/POST telemetry."""

    @method_decorator(require_login)
    def post(self, request):
        """Posts the UAS position with a POST request.

        User must send a POST request with the following paramters:
        latitude: A latitude in decimal degrees.
        longitude: A logitude in decimal degrees.
        altitude_msl: An MSL altitude in decimal feet.
        uas_heading: The UAS (true north) heading in decimal degrees.
        """
        try:
            # Get the parameters
            latitude = float(request.POST['latitude'])
            longitude = float(request.POST['longitude'])
            altitude_msl = float(request.POST['altitude_msl'])
            uas_heading = float(request.POST['uas_heading'])
        except KeyError:
            # Failed to get POST parameters
            logger.warning(
                'User did not specify all params for uas telemetry request.')
            logger.debug(request)
            return HttpResponseBadRequest(
                'Posting UAS position must contain POST parameters "latitude", '
                '"longitude", "altitude_msl", and "uas_heading".')
        except ValueError:
            # Failed to convert parameters
            logger.warning(
                'User specified a param which could not converted to an ' +
                'appropriate type.')
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
