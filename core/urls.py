from django.conf.urls import url, include

from . import views

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^api/devices', views.device_list),
    url(r'^api/devices/(?P<pk>[0-9]+)/$', views.device_detail),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]