from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

admin.autodiscover()

# yapf: disable
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('auvsi_suas.views.urls', namespace="auvsi_suas")),
]
# yapf: enable
