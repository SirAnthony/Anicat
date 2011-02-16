from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'anime.views',
    (r'^$', 'index'),
    (r'^(?P<page>\d+)/?$', 'index'),
    (r'^changes/$', 'changes'),
    (r'^add/$', 'add'),
    (r'^ajax/login/$', 'ajaxlogin'),
    (r'^logout/$', 'logout'),
    (r'^(?P<anime_id>\d+)/$', 'info'),
)
#
