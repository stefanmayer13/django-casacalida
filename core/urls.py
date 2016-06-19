from django.conf.urls import url, include

from . import views

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^api/v1/check/$', views.api_check),
    url(r'^api/v1/fullupdate/$', views.api_full_update),
    url(r'^api/v1/incrementalupdate/$', views.api_incremental_update),
    url(r'^api/devices/$', views.device_list),
    url(r'^api/devices/(?P<id>[0-9]+)/$', views.device_detail)
]