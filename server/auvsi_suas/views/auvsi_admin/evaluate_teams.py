"""Admin automatic evaluation of teams view."""

import cStringIO
import csv
import json
import zipfile
from auvsi_suas.models.mission_config import MissionConfig
from auvsi_suas.views import logger
from auvsi_suas.views.decorators import require_superuser
from auvsi_suas.views.missions import mission_for_request
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.generic import View


class EvaluateTeams(View):
    """Evaluates the teams and returns a zip file with CSV & JSON data.

    Zip file contains a master CSV and JSON file with all evaluation data.
    It also contains per-team JSON files for individual team feedback.
    """

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(EvaluateTeams, self).dispatch(*args, **kwargs)

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
        user_eval_data = mission.evaluate_teams(users)
        if not user_eval_data:
            logger.warning('No data for team evaluation.')
            return HttpResponseServerError(
                'Could not get user evaluation data.')

        # Convert to username key-d map.
        user_eval_data = {u.username: e for u, e in user_eval_data.iteritems()}

        # Get JSON output.
        json_data = {u: e.json() for u, e in user_eval_data.iteritems()}

        # Get CSV output.
        user_col_data = {u: e.csv() for u, e in user_eval_data.iteritems()}
        col_headers = set()
        for col_data in user_col_data.values():
            for header in col_data.keys():
                col_headers.add(header)
        col_headers = sorted(col_headers)
        csv_io = cStringIO.StringIO()
        writer = csv.DictWriter(csv_io, fieldnames=col_headers)
        writer.writeheader()
        for col_data in user_col_data.values():
            writer.writerow(col_data)
        csv_output = csv_io.getvalue()
        csv_io.close()

        # Form Zip file.
        zip_io = cStringIO.StringIO()
        with zipfile.ZipFile(zip_io, 'w') as zip_file:
            zip_file.writestr('/evaluate_teams/all.csv', csv_output)
            zip_file.writestr('/evaluate_teams/all.json',
                              json.dumps(json_data,
                                         indent=4))
            for u, e in json_data.iteritems():
                zip_file.writestr('/evaluate_teams/teams/%s.json' % u,
                                  json.dumps(e,
                                             indent=4))
        zip_output = zip_io.getvalue()
        zip_io.close()

        return HttpResponse(zip_output, content_type='application/zip')
