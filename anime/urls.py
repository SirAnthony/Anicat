from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'anime.views',
    (r'^$', 'index'),
    (r'^(?P<page>\d+)/?$', 'index'),
    (r'^changes/$', 'changes'),
    (r'^add/$', 'add'),
    (r'^logout/$', 'logout'),
    (r'^register/$', 'register'),
    (r'^card/(?P<animeId>\d+)?/?$', 'card'),
    (r'^stat/(?P<userId>\d+)?/?$', 'stat'),
    (r'^test/$', 'test'),
)

urlpatterns += patterns('anime.ajax',
    (r'^ajax/get/$', 'get'),
    (r'^ajax/set/$', 'change'),
    (r'^ajax/login/$', 'login'),
    (r'^ajax/register/$', 'register'),
)

urlpatterns += patterns('',
    (r'^jsi18n/(?P<packages>\S+?)?/?$', 'django.views.i18n.javascript_catalog'),
)
#