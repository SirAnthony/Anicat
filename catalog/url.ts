
import url = require('urlreverser').url;
import routes = require('./routes');
export var E = {};
interface LinkData {
    renderer: Renderer,
    url: string,
};

// TODO: links can be generated using type information

var url_default = [
    // General
    [url('^card/(?:(?P<id>\d+)/)?$', 'card'), routes.card],
    // General
    ['^$', routes.index],
    [url('^(?:user/(?P<user>\d+)/)?(?:show/(?P<status>\d+)/)?'+
         '(?:sort/(?P<order>-?\w+)/)?(?:(?P<page>\d+)/)?$', 'index'),
         routes.index],
    [url('^requests/(?:status/(?P<status>\d+)/)?(?:type/(?P<rtype>\d+)/)?'+
         '(?:(?P<page>\d+)/)?$', 'requests'), routes.requests],
    [url('^search/(?:(?P<string>.+?)/(?:sort/(?P<order>-?\w+)/)?'+
         '(?:limit/(?P<limit>\d+)/)?(?:(?P<page>\d+)/)?)?$', 'search'),
         routes.search],
    //# Direct
    [url('^changes/$', 'changes'), routes.direct, {template: 'anime/changes.html'}],
    [url('^faq/$', 'faq'), routes.direct, {template: 'anime/faq.html'}],
    [url('^blank/$' 'blank'), routes.direct, {template: 'anime/blank.html'}],
    // # History
    //url(r'^history/(?:(?P<model>[a-zA-Z]+)/)?(?:show/(?P<status>\w)/)?(?:sort/(?P<order>-?\w+)/)?(?:(?P<page>\d+)/)?$',
    //HistoryListView.as_view(), name='history'),
    // User
    [url('^css/$', 'user_css'), routes.user.css],
    [url('^settings/$', 'settings'), routes.user.settings],
    [url('^stat/(?:(?P<user_id>\d+)/)?$', 'statistics'), routes.user.stat],
    [url('^stat/export/?$', 'statistics_export'), router.user.export],
    [url('^login/$', 'login'), routes.user.login],
    [url('^login/error/$', 'login_error'), routes.user.error],
    [url('^logout/$', 'logout'), routes.user.logout],
    [url('^register/$', 'register'), routes.user.register],
)

/*
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
*/

function prepare(link: string,renderer: Renderer, opt){
    var instance : Renderer = renderer(opt);
    return LinkData(instance, template, link);
}

E.init = function init(list) : LinkData[] {
    list = list||url_default;
    return list.map((data) => {
        return prepare.apply(null, data); });
}
