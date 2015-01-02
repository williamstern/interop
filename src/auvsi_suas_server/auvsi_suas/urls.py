from django.conf.urls import patterns, url
from auvsi_suas import views

urlpatterns = patterns('',
    # Team interoperability
    url(r'^api/login$', views.loginUser, name='login'),
    url(r'^api/interop/server_info$', views.getServerInfo, name='server_info'),
    url(r'^api/interop/obstacles$', views.getObstacles, name='obstacles'),
    url(r'^api/interop/uas_telemetry$', views.postUasPosition,
        name='uas_telemetry'),

    # Admin access views
    url(r'^$', views.indexView, name='index'),
    url(r'^auvsi_admin/evaluate_teams.csv$', views.evaluateTeams,
        name='evaluate_teams'),
)

