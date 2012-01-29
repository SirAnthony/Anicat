from django.conf import settings
from django.conf.urls.defaults import patterns, url

from django.views.generic.simple import direct_to_template

from anime.forms.User import NotActivePasswordResetForm


urlpatterns = patterns(
    'anime.views',
    (r'^$', 'index'),
    # TODO Split regexp
    (r'^(user/(?P<user>\d+))?/?(show/(?P<status>\d+))?/?(sort/(?P<order>-?\w+))?/?(?P<page>\d+)?/$', 'index'),
    url(r'^search/(?P<string>[^/]+)?/?(field/(?P<field>\w+))?/?(sort/(?P<order>\w+))?/?(?P<page>\d+)?/?$', 'search', name='search'),
    (r'^changes/$', direct_to_template, {'template': 'anime/changes.html'}, 'changes'),
    (r'^faq/$', direct_to_template, {'template': 'anime/faq.html'}, 'faq'),
    url(r'^card/(?P<animeId>\d+)?/?$', 'card', name='card'),
    url(r'^stat/(?P<userId>\d+)?/?$', 'stat', name='statistics'),
    # TODO Split regexp
    url(r'^requests/(status/(?P<status>\d+))?/?(type/(?P<rtype>\d+))?/?(?P<page>\d+)?/?$', 'requests', name='requests'),
    url(r'^css/$', 'generateCss', name='user_css'),
    (r'^test/$', 'test'),
    (r'^history/add/?(f/(?P<field>\w+))?/?(?P<page>\d+)?/$', 'history'),
)

urlpatterns += patterns('anime.userviews',
    url(r'^login/$', 'login', name='login'),
    (r'^login/error/$', 'social_error'),
    (r'^login/done/$', direct_to_template, {'template': 'anime/user/social-done.html'}),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^register/$', 'register', name='registration'),
    url(r'^settings/$', 'settings', name='settings'),
)

# Password functions
urlpatterns += patterns('django.contrib.auth.views',
    (r'^password/reset/$', 'password_reset', {
        'post_reset_redirect': '/password/reset/sent/',
        'email_template_name': 'anime/user/password_reset_email.html',
        'template_name': 'anime/user/password.html',
        'password_reset_form': NotActivePasswordResetForm,},
        'password_reset'),
    (r'^password/reset/sent/$', direct_to_template, {
        'template': 'anime/user/password_reset_sent.html'}),
    (r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'password_reset_confirm', {
        'template_name': 'anime/user/password_reset_confirm.html',
        'post_reset_redirect': '/password/reset/done/'},
        'password_reset_confirm'),
    (r'^password/reset/done/$', 'password_reset_complete',
        {'template_name': 'anime/user/password_reset_complete.html'}),
    (r'^password/change/$', 'password_change', {
        'post_change_redirect': '/settings/',
        'template_name': 'anime/user/password.html'}, 'password_change'),
)

urlpatterns += patterns('anime.editview',
    url(r'^add/$', 'add', name='edit_add'),
    (r'^feedback/$', 'feedback'),
    (r'^animerequest/$', 'anime_request'),
    url(r'^request/(?P<request_id>\d+)/?$', 'request_item', name='request_item'),
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

urlpatterns += patterns('anime.socialviews',
    url(r'^complete/(?P<backend>[^/]+)/$', 'complete', name='socialauth_complete'),
)

urlpatterns += patterns('social_auth.views',
    url(r'^login/(?P<backend>[^/]+)/$', 'auth', name='socialauth_begin'),
    url(r'^associate/(?P<backend>[^/]+)/$', 'associate', name='socialauth_associate_begin'),
    url(r'^associate/complete/(?P<backend>[^/]+)/$', 'associate_complete',
        name='socialauth_associate_complete'),
    url(r'^disconnect/(?P<backend>[^/]+)/$', 'disconnect', name='socialauth_disconnect'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$', 'disconnect',
        name='socialauth_disconnect_individual'),
)

urlpatterns += patterns('',
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
