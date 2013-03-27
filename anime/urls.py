
from django.conf import settings

try:
    from django.conf.urls import patterns, url, include
except ImportError:
    # for Django version less then 1.4
    from django.conf.urls.defaults import patterns, url, include

from django.views.generic.base import TemplateView

from anime.forms.User import NotActivePasswordResetForm
from anime.views.list import RequestsListView
from anime.views.ajaxlist import IndexListView, SearchListView
from anime.views.history import HistoryListView


# General
urlpatterns = patterns(
    'anime.views.base',
    # TODO Split regexp
    url(r'^card/(?:(?P<anime_id>\d+)/)?$', 'card', name='card'),
)

# Classes
urlpatterns += patterns('',
    (r'^$', IndexListView.as_view()),
    url(r'^(?:user/(?P<user>\d+)/)?(?:show/(?P<status>\d+)/)?(?:sort/(?P<order>-?\w+)/)?(?:(?P<page>\d+)/)?$',
        IndexListView.as_view(), name='index'),
    # TODO Split regexp
    url(r'^requests/(?:status/(?P<status>\d+)/)?(?:type/(?P<rtype>\d+)/)?(?:(?P<page>\d+)/)?$',
        RequestsListView.as_view(), name='requests'),
    url(r'^search/(?:(?P<string>[^/]+)/(?:sort/(?P<order>-?\w+)/)?(?:limit/(?P<limit>\d+)/)?(?:(?P<page>\d+)/)?)?$',
        SearchListView.as_view(), name='search'),
)

# Direct
urlpatterns += patterns('',
    url(r'^changes/$', TemplateView.as_view(template_name='anime/changes.html'), name='changes'),
    url(r'^faq/$', TemplateView.as_view(template_name='anime/faq.html'), name='faq'),
    url(r'^blank/$', TemplateView.as_view(template_name='anime/blank.html'), name='blank'),
)

# History
urlpatterns += patterns('anime.views.history',
    url(r'^history/(?:(?P<model>[a-zA-Z]+)/)?(?:show/(?P<status>\w)/)?(?:sort/(?P<order>-?\w+)/)?(?:(?P<page>\d+)/)?$',
    HistoryListView.as_view(), name='history'),
)

# User
urlpatterns += patterns('anime.views.user',
    url(r'^login/$', 'login', name='login'),
    url(r'^login/error/$', 'social_error', name='social_error'),
    (r'^login/done/$', TemplateView.as_view(template_name='anime/user/social-done.html')),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^register/$', 'register', name='registration'),
    url(r'^settings/$', 'settings', name='settings'),
    url(r'^stat/(?:(?P<user_id>\d+)/)?$', 'statistics', name='statistics'),
    url(r'^stat/export/?$', 'statistics_export', name='statistics_export'),
    url(r'^css/$', 'generate_css', name='user_css'),
)

# Password functions
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^password/reset/$', 'password_reset', {
        'post_reset_redirect': '/password/reset/sent/',
        'subject_template_name': 'anime/user/password_reset_subject.txt',
        'email_template_name': 'anime/user/password_reset_email.html',
        'template_name': 'anime/user/password.html',
        'password_reset_form': NotActivePasswordResetForm,},
        name='password_reset'),
    (r'^password/reset/sent/$', TemplateView.as_view(
        template_name='anime/user/password_reset_sent.html')),
    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'password_reset_confirm', {
        'template_name': 'anime/user/password_reset_confirm.html',
        'post_reset_redirect': '/password/reset/done/'},
        name='password_reset_confirm'),
    (r'^password/reset/done/$', 'password_reset_complete',
        {'template_name': 'anime/user/password_reset_complete.html'}),
    url(r'^password/change/$', 'password_change', {
        'post_change_redirect': '/settings/',
        'template_name': 'anime/user/password.html'},
        name='password_change'),
)

# Edit
urlpatterns += patterns('anime.views.edit',
    url(r'^add/$', 'add', name='edit_add'),
    url(r'^feedback/$', 'feedback', name='edit_feedback'),
    url(r'^animerequest/$', 'anime_request', name='edit_animerequest'),
    url(r'^request/(?P<request_id>\d+)/?$', 'request_item', name='request_item'),
    url(r'^edit/(?P<model>[a-zA-Z_]+)/(?P<item_id>\d+)/(?:(?P<field>[a-zA-Z_,]+)/)?$',
        'edit', name='edit_item'),
)

# Ajax
urlpatterns += patterns('anime.views.ajax',
    url(r'^ajax/get/$', 'get', name='ajax_get'),
    url(r'^ajax/set/$', 'change', name='ajax_set'),
    url(r'^ajax/filter/$', 'afilter', name='ajax_filter'),
    url(r'^ajax/form/$', 'form', name='ajax_form'),
    url(r'^ajax/add/$', 'add', name='ajax_add'),
    url(r'^ajax/login/$', 'login', name='ajax_login'),
    url(r'^ajax/register/$', 'register', name='ajax_register'),
    url(r'^ajax/stat/$', 'statistics', name='ajax_statistics'),
)

#Ajax classes
urlpatterns += patterns('',
    url(r'^ajax/list/$', IndexListView.as_view(ajax_call=True), name='ajax_list'),
    url(r'^ajax/search/$', SearchListView.as_view(ajax_call=True), name='ajax_search'),
)

urlpatterns += patterns('', #'social_auth.views',
    #~ url(r'^login/(?P<backend>[^/]+)/$', 'auth', name='socialauth_begin'),
    #~ url(r'^complete/(?P<backend>[^/]+)/$', 'complete', name='socialauth_complete'),
    #~ url(r'^associate/(?P<backend>[^/]+)/$', 'associate', name='socialauth_associate_begin'),
    #~ url(r'^associate/complete/(?P<backend>[^/]+)/$', 'associate_complete',
        #~ name='socialauth_associate_complete'),
    #~ url(r'^disconnect/(?P<backend>[^/]+)/$', 'disconnect', name='socialauth_disconnect'),
    #~ url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$', 'disconnect',
        #~ name='socialauth_disconnect_individual'),
    url(r'', include('social_auth.urls')),
)


urlpatterns += patterns('',
    (r'^jsi18n/(?P<packages>\S+?)?/?$',
        'django.views.i18n.javascript_catalog'),
)

if not settings.DEPLOY:
    urlpatterns += patterns('', url(r'^media/(.*)$',
        'django.views.static.serve', kwargs={
        'document_root': settings.MEDIA_ROOT}),
                                url(r'^images/(.*)$',
        'django.views.static.serve', kwargs={
        'document_root': settings.IMAGES_ROOT}),
                                url(r'^static/(.*)$',
        'django.views.static.serve', kwargs={
        'document_root': settings.STATIC_ROOT}),
    )
