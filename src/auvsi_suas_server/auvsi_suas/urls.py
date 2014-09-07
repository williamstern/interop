from django.conf.urls import patterns, url
from auvsi_suas import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^api/login$', views.loginUser, name='login'),
    url(r'^api/interop/server_info$', views.getServerInfo, name='server_info'),
    url(r'^api/interop/obstacle$', views.getObstacles, name='obstacle'),
    url(r'^api/interop/uas_telemetry', views.updateUasPosition,
        name='uas_telemetry')
)

