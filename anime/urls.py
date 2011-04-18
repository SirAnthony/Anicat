from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'anime.views',
    (r'^$', 'index'),
    (r'^(show/(?P<status>\d+))?/?(sort/(?P<order>\w+))?/?(?P<page>\d+)?/$', 'index'),
    (r'^changes/$', 'changes'),
    (r'^add/$', 'add'),
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^register/$', 'register'),
    (r'^card/(?P<animeId>\d+)?/?$', 'card'),
    (r'^stat/(?P<userId>\d+)?/?$', 'stat'),
    (r'^css/$', 'generateCss'),
    (r'^test/$', 'test'),
    (r'^search/$', 'blank'),
    (r'^history/add/?/?(f/(?P<field>\w+))?/?(?P<page>\d+)?/$', 'history'),
    (r'^settings/$', 'settings')
)

urlpatterns += patterns('anime.ajax',
    (r'^ajax/get/$', 'get'),
    (r'^ajax/set/$', 'change'),
    (r'^ajax/add/$', 'add'),
    (r'^ajax/login/$', 'login'),
    (r'^ajax/register/$', 'register'),
    (r'^ajax/search/$', 'search'),
)

urlpatterns += patterns('',
    (r'^jsi18n/(?P<packages>\S+?)?/?$', 'django.views.i18n.javascript_catalog'),
)
#