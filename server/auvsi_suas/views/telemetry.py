"""Telemetry view."""

import iso8601
import json
from auvsi_suas.models import UasTelemetry
from auvsi_suas.views import logger
from auvsi_suas.views.decorators import require_superuser
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.generic import View


class Telemetry(View):
    """Gets a list of all telemetry."""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(Telemetry, self).dispatch(*args, **kwargs)

    def get(self, request):
        limit = 100
        user = None
        since = None
        before = None

        if 'limit' in request.GET:
            try:
                limit = int(request.GET['limit'])
            except (TypeError, ValueError):
                return HttpResponseBadRequest("Invalid limit '%s'" % \
                                                request.GET['limit'])

        if 'user' in request.GET:
            try:
                user_id = int(request.GET['user'])
            except (TypeError, ValueError):
                return HttpResponseBadRequest("Invalid user '%s'" % \
                                                request.GET['user'])
            try:
                user = User.objects.filter(pk=user_id).get()
            except User.DoesNotExist:
                return HttpResponseBadRequest("Unknown user '%s'" % \
                                                request.GET['user'])

        # since is non-inclusive
        if 'since' in request.GET:
            try:
                since = iso8601.parse_date(request.GET['since'])
            except iso8601.ParseError:
                return HttpResponseBadRequest("Bad timestamp '%s'" % \
                                                request.GET['since'])

        # before is non-inclusive
        if 'before' in request.GET:
            try:
                before = iso8601.parse_date(request.GET['before'])
            except iso8601.ParseError:
                return HttpResponseBadRequest("Bad timestamp '%s'" % \
                                                request.GET['before'])

        # Prefetch data from all ForeignKeys (e.g., AerialPosition) when
        # evaluating the query.  This allows us to avoid making hundreds
        # of other queries as we access all of those fields.
        query = UasTelemetry.objects.select_related()

        if user:
            query = query.filter(user=user)

        if since:
            query = query.filter(timestamp__gt=since)

        if before:
            query = query.filter(timestamp__lt=before)

        logs = query.order_by('-timestamp').all()[:limit]

        response = [l.json() for l in logs]

        return HttpResponse(json.dumps(response),
                            content_type="application/json")
