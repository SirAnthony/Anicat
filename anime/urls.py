from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'anime.views',
    (r'^$', 'index'),
    (r'^(?P<page>\d+)/?$', 'index'),
    (r'^changes/$', 'changes'),
    (r'^add/$', 'add'),
    (r'^ajax/get/$', 'get'),
    (r'^ajax/login/$', 'ajaxlogin'),
    (r'^ajax/register/$', 'ajaxregister'),    
    (r'^logout/$', 'logout'),
    (r'^register/$', 'register'),
    (r'^/card/(?P<anime_id>\d+)/?$', 'card'),
)
#
