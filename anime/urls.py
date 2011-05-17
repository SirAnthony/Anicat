from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    'anime.views',
    (r'^$', 'index'),
    (r'^(show/(?P<status>\d+))?/?(sort/(?P<order>\w+))?/?(?P<page>\d+)?/$', 'index'),
    (r'^search/(?P<string>[^/]+)?/?(field/(?P<field>\w+))?/?(sort/(?P<order>\w+))?/?(?P<page>\d+)?/?$', 'search'),
    (r'^changes/$', direct_to_template, {'template': 'anime/changes.html'}),
    (r'^faq/$', direct_to_template, {'template': 'anime/faq.html'}),
    (r'^card/(?P<animeId>\d+)?/?$', 'card'),
    (r'^stat/(?P<userId>\d+)?/?$', 'stat'),
    (r'^css/$', 'generateCss'),
    (r'^test/$', 'test'),
    (r'^history/add/?/?(f/(?P<field>\w+))?/?(?P<page>\d+)?/$', 'history'),
)

urlpatterns += patterns('anime.userviews',
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^register/$', 'register'),
    (r'^settings/$', 'settings')
)

urlpatterns += patterns('anime.editview',
    (r'^add/$', 'add'),
    (r'^edit/(?P<model>[a-zA-Z_]+)?/?(?P<itemId>\d+)/?(?P<field>[a-zA-Z_,]+)?/?$', 'edit'),
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