from django.conf.urls import url, include

from . import views
from . import apis

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),

    url(r'^seton/$', views.seton),
    url(r'^setoff/$', views.setoff),

    url(r'^api/v1/csrf/$', apis.csrf),
    url(r'^api/v1/login/$', apis.login),
    url(r'^api/v1/messages/(?P<language>[a-zA-Z\-_]+)$', apis.messages),
    url(r'^api/v1/devices/$', apis.device_list),
    url(r'^api/v1/sensors/(?P<sensorid>[0-9]+)/$', apis.sensor_detail),

    url(r'^api/v1/check/$', views.api_check),
    url(r'^api/v1/fullupdate/$', views.api_full_update),
    url(r'^api/v1/incrementalupdate/$', views.api_incremental_update),
]