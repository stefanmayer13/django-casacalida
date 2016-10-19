from django.conf.urls import url, include

from . import views
from . import apis

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^enabledaily/$', views.enabledaily),
    url(r'^skipdaily/$', views.skipdaily),
    url(r'^settime/$', views.settime),
    url(r'^seton/$', views.seton),
    url(r'^setoff/$', views.setoff),
    url(r'^api/v1/csrf/$', apis.csrf),
    url(r'^api/v1/login/$', apis.login),
    url(r'^api/v1/time/$', views.get_time),
    url(r'^api/v1/check/$', views.api_check),
    url(r'^api/v1/fullupdate/$', views.api_full_update),
    url(r'^api/v1/incrementalupdate/$', views.api_incremental_update),
    url(r'^api/v1/devices/$', apis.device_list),
    url(r'^api/v1/devices/(?P<deviceid>[0-9]+)/$', views.device_detail)
]