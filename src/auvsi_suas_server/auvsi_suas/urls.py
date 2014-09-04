from django.conf.urls import patterns, url
from auvsi_suas import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)

