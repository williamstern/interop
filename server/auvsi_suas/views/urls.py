from auvsi_suas.views.login import Login
from auvsi_suas.views.index import Index
from auvsi_suas.views.missions import Evaluate
from auvsi_suas.views.missions import ExportKml
from auvsi_suas.views.missions import LiveKml
from auvsi_suas.views.missions import LiveKmlUpdate
from auvsi_suas.views.missions import Missions
from auvsi_suas.views.missions import MissionsId
from auvsi_suas.views.odlcs import Odlcs
from auvsi_suas.views.odlcs import OdlcsAdminReview
from auvsi_suas.views.odlcs import OdlcsId
from auvsi_suas.views.odlcs import OdlcsIdImage
from auvsi_suas.views.teams import Teams
from auvsi_suas.views.teams import Team
from auvsi_suas.views.telemetry import Telemetry
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

app_name = 'auvsi_suas'

# yapf: disable
urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^api/login$', Login.as_view(), name='login'),
    url(r'^api/missions$', Missions.as_view(), name='missions'),
    url(r'^api/missions/(?P<pk>\d+)$', MissionsId.as_view(), name='missions_id'),
    url(r'^api/missions/(?P<pk>\d+)/evaluate\.zip$', Evaluate.as_view(), name='evaluate'),
    url(r'^api/missions/export\.kml$', ExportKml.as_view(), name='export_kml'),
    url(r'^api/missions/live\.kml$', LiveKml.as_view(), name='live_kml'),
    url(r'^api/missions/update\.kml$', LiveKmlUpdate.as_view(), name='update_kml'),
    url(r'^api/odlcs$', Odlcs.as_view(), name='odlcs'),
    url(r'^api/odlcs/(?P<pk>\d+)$', OdlcsId.as_view(), name='odlcs_id'),
    url(r'^api/odlcs/(?P<pk>\d+)/image$', OdlcsIdImage.as_view(), name='odlcs_id_image'),
    url(r'^api/odlcs/review$', OdlcsAdminReview.as_view(), name='odlcs_review'),
    url(r'^api/odlcs/review/(?P<pk>\d+)$', OdlcsAdminReview.as_view(), name='odlcs_review_id'),
    url(r'^api/teams$', Teams.as_view(), name='teams'),
    url(r'^api/teams/(?P<username>.+)$', Team.as_view(), name='team'),
    url(r'^api/telemetry$', Telemetry.as_view(), name='telemetry'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# yapf: enable
