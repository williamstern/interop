"""Targets view."""
import json
from auvsi_suas.models import GpsPosition, Target, TargetType, Color, Shape, Orientation
from auvsi_suas.views import logger
from auvsi_suas.views.decorators import require_login
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View


def normalize_data(data):
    """Convert received target parameters to native Python types.

    Checks whether values are valid and in-range. Skips any non-existent
    fields.

    Args:
        data: JSON-converted dictionary of target parameters

    Returns:
        data dictionary with all present target fields in native types.

    Raises:
        ValueError: Parameter not convertable or out-of-range
    """

    # 'alphanumeric' and 'description' require no conversion.

    if 'type' in data:
        try:
            data['type'] = TargetType.lookup(data['type'])
        except KeyError:
            raise ValueError('Unknown target type "%s"; known types %r' %
                             (data['type'], TargetType.names()))

    if 'latitude' in data:
        try:
            data['latitude'] = float(data['latitude'])
            if data['latitude'] < -90 or data['latitude'] > 90:
                raise ValueError
        except ValueError:
            # Unable to convert to float or out-of-range
            raise ValueError('Invalid latitude "%s", must be -90 <= lat <= 90'
                             % data['latitude'])

    if 'longitude' in data:
        try:
            data['longitude'] = float(data['longitude'])
            if data['longitude'] < -180 or data['longitude'] > 180:
                raise ValueError
        except ValueError:
            # Unable to convert to float or out-of-range
            raise ValueError(
                'Invalid longitude "%s", must be -180 <= lat <= 180' %
                (data['longitude']))

    if 'orientation' in data:
        try:
            data['orientation'] = Orientation.lookup(data['orientation'])
        except KeyError:
            raise ValueError('Unknown orientation "%s"; known orientations %r'
                             % (data['orientation'], Orientation.names()))

    if 'shape' in data:
        try:
            data['shape'] = Shape.lookup(data['shape'])
        except KeyError:
            raise ValueError('Unknown shape "%s"; known shapes %r' %
                             (data['shape'], Shape.names()))

    if 'background_color' in data:
        try:
            data['background_color'] = Color.lookup(data['background_color'])
        except KeyError:
            raise ValueError('Unknown color "%s"; known colors %r' %
                             (data['background_color'], Color.names()))

    if 'alphanumeric_color' in data:
        try:
            data['alphanumeric_color'] = \
                Color.lookup(data['alphanumeric_color'])
        except KeyError:
            raise ValueError('Unknown color "%s"; known colors %r' %
                             (data['alphanumeric_color'], Color.names()))

    return data


class Targets(View):
    """POST new target."""

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(Targets, self).dispatch(*args, **kwargs)

    def post(self, request):
        data = json.loads(request.body)

        # Target type is required.
        if 'type' not in data:
            return HttpResponseBadRequest('Target type required.')

        # Require zero or both of latitude and longitude.
        if ('latitude' in data and 'longitude' not in data) or \
            ('latitude' not in data and 'longitude' in data):
            return HttpResponseBadRequest(
                'Either none or both of latitude and longitude required.')

        try:
            data = normalize_data(data)
        except ValueError as e:
            return HttpResponseBadRequest(str(e))

        l = None
        if 'latitude' in data and 'longitude' in data:
            l = GpsPosition(latitude=data['latitude'], longitude=data['longitude'])
            l.save()

        # Use the dictionary get() method to default non-existent values to None.
        t = Target(user=request.user,
                   target_type=data['type'],
                   location=l,
                   orientation=data.get('orientation'),
                   shape=data.get('shape'),
                   background_color=data.get('background_color'),
                   alphanumeric=data.get('alphanumeric', ''),
                   alphanumeric_color=data.get('alphanumeric_color'),
                   description=data.get('description', ''))
        t.save()

        return JsonResponse(t.json(), status=201)
