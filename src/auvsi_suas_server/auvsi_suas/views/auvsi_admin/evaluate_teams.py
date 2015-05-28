"""Admin automatic evaluation of teams view."""

import copy
import cStringIO
import csv
from auvsi_suas.models import MissionConfig
from auvsi_suas.views import logger
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.http import HttpResponseServerError


@user_passes_test(lambda u: u.is_superuser)
def getTeamEvaluationCsv(request):
    """Evaluates the teams by forming a CSV containing useful stats."""
    logger.info('Admin downloaded team evaluation.')
    # Get the mission for evaluation
    missions = MissionConfig.objects.all()
    if not missions or not missions[0]:
        logger.error('No mission defined for which to evaluate teams.')
        return HttpResponseServerError('No mission defined.')
    if len(missions) > 1:
        logger.warning('More than one mission defined, taking first.')
    mission = missions[0]
    # Get the eval data for the teams
    user_eval_data = mission.evaluateTeams()
    if not user_eval_data:
        logger.warning('No data for team evaluation.')
        return HttpResponseServerError('Could not get user evaluation data.')
    # Reformat to column oriented
    user_col_data = dict()
    for (user, eval_data) in user_eval_data.iteritems():
        col_data = user_col_data.setdefault(user, dict())
        col_data['username'] = user.username
        work_queue = [([], eval_data)]
        while len(work_queue) > 0:
            (cur_prefixes, cur_map) = work_queue.pop()
            for (key, val) in cur_map.iteritems():
                new_prefixes = copy.copy(cur_prefixes)
                new_prefixes.append(str(key))
                if isinstance(val, dict):
                    work_queue.append((new_prefixes, val))
                else:
                    column_key = '.'.join(new_prefixes)
                    col_data[column_key] = val
    # Get column headers
    col_headers = set()
    for col_data in user_col_data.values():
        for header in col_data.keys():
            col_headers.add(header)
    col_headers = sorted(col_headers)
    # Write output
    csv_output = cStringIO.StringIO()
    writer = csv.DictWriter(csv_output, fieldnames=col_headers)
    writer.writeheader()
    for col_data in user_col_data.values():
        writer.writerow(col_data)
    output = csv_output.getvalue()
    csv_output.close()
    return HttpResponse(output)
