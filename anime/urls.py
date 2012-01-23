from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    'anime.views',
    (r'^$', 'index'),
    # TODO Split regexp
    (r'^(user/(?P<user>\d+))?/?(show/(?P<status>\d+))?/?(sort/(?P<order>-?\w+))?/?(?P<page>\d+)?/$', 'index'),
    (r'^search/(?P<string>[^/]+)?/?(field/(?P<field>\w+))?/?(sort/(?P<order>\w+))?/?(?P<page>\d+)?/?$', 'search'),
    (r'^changes/$', direct_to_template, {'template': 'anime/changes.html'}),
    (r'^faq/$', direct_to_template, {'template': 'anime/faq.html'}),
    (r'^card/(?P<animeId>\d+)?/?$', 'card'),
    (r'^stat/(?P<userId>\d+)?/?$', 'stat'),
    # TODO Split regexp
    (r'^requests/(status/(?P<status>\d+))?/?(type/(?P<rtype>\d+))?/?(?P<page>\d+)?/?$', 'requests'),
    (r'^css/$', 'generateCss'),
    (r'^test/$', 'test'),
    (r'^history/add/?/?(f/(?P<field>\w+))?/?(?P<page>\d+)?/$', 'history'),
)

urlpatterns += patterns('anime.userviews',
    (r'^login/$', 'login'),
    (r'^login/error/$', 'social_error'),
    (r'^login/done/$', direct_to_template, {'template': 'anime/social-done.html'}),
    (r'^logout/$', 'logout'),
    (r'^register/$', 'register'),
    (r'^settings/$', 'settings'),
)

urlpatterns += patterns('anime.editview',
    (r'^add/$', 'add'),
    (r'^feedback/$', 'feedback'),
    (r'^animerequest/$', 'anime_request'),
    (r'^request/(?P<requestId>\d+)/?$', 'request_item'),
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
    (r'', include('social_auth.urls')),
    (r'^jsi18n/(?P<packages>\S+?)?/?$',
        'django.views.i18n.javascript_catalog'),
)

if settings.DEBUG:
    urlpatterns += patterns('', url(r'^media/(.*)$',
        'django.views.static.serve', kwargs={
        'document_root': settings.MEDIA_ROOT}),
                                url(r'^images/(.*)$',
        'django.views.static.serve', kwargs={
        'document_root': settings.IMAGES_ROOT}), )
