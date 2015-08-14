from auvsi_suas.views import clear_cache
from auvsi_suas.views import missions
from auvsi_suas.views import teams
from auvsi_suas.views import telemetry
from auvsi_suas.views.auvsi_admin import evaluate_teams
from auvsi_suas.views.auvsi_admin import export_kml
from auvsi_suas.views.auvsi_admin import live_kml
from auvsi_suas.views.auvsi_admin import index
from auvsi_suas.views.interop import login
from auvsi_suas.views.interop import obstacles
from auvsi_suas.views.interop import server_info
from auvsi_suas.views.interop import uas_telemetry
from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static


# yapf: disable
urlpatterns = patterns(
    '',
    # Team interoperability
    url(r'^api/login$', login.login_user, name='login'),
    url(r'^api/interop/server_info$', server_info.server_info,
        name='server_info'),
    url(r'^api/interop/obstacles$', obstacles.obstacles, name='obstacles'),
    url(r'^api/interop/uas_telemetry$', uas_telemetry.post_uas_position,
        name='uas_telemetry'),
    # Admin API
    url(r'^api/missions$', missions.missions, name='missions'),
    url(r'^api/teams$', teams.teams, name='teams'),
    url(r'^api/teams/(?P<pk>\d+)$', teams.teams_id, name='teams_id'),
    url(r'^api/telemetry$', telemetry.telemetry, name='telemetry'),
    url(r'^api/clear_cache$', clear_cache.clear_cache, name='clear_cache'),
    # Admin access views
    url(r'^$', index.index, name='index'),
    url(r'^auvsi_admin/evaluate_teams.csv$', evaluate_teams.team_evaluation_csv,
        name='evaluate_teams'),
    url(
        r'^auvsi_admin/export_data.kml$',
        export_kml.generate_kml,
        name='export_data',
    ),
    url(
        r'^auvsi_admin/live.kml$',
        live_kml.generate_kml,
        name='live_kml',
    ),
    url(
        r'^auvsi_admin/update.kml$',
        live_kml.generate_live_kml,
        name='update_kml',
    ),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# yapf: enable
