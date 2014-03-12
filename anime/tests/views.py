
import json
import os

from django.conf import settings
from django.core.urlresolvers import reverse

from anime import api
from anime.utils import cache
from anime.utils.cache import invalidate_key
from anime.models import AnimeItem, AnimeBundle, AnimeRequest, EDIT_MODELS
from anime.tests._classes import CleanTestCase as TestCase
from anime.tests._functions import (fake_request, create_user, login,
                            fill_params, create_cachestr, hexdigest)
from anime.utils.catalog import last_record_pk


BLANK_CACHESTR = create_cachestr()
#'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'


class AjaxTest(TestCase):

    fixtures = ['2trash.json']

    def send_request(self, link, params, returns):
        response = self.client.post(link, params)
        ret = json.loads(response._container[0])
        self.check_response(ret, returns)
        return ret

    @create_user()
    def setUp(self):
        pass

    def tearDown(self):
        searchkey = '38e442f57cd588f5e52f1484b1bc67c480df31ae'
        cache.delete('ajaxsearch:%s' % searchkey)
        invalidate_key('search', searchkey)
        for key in ['47585a4c37e8f7c9845f97099debf576fe46fb92',
                    '66811e1a68035d2514733b54be7e9fc7e98d5a2e',
                    '4c2730ba7c3198ec39fadb22988623e2be0dd908',
                    '8ccbb6ff42daa120dd76e2beec460b282d8ed746']:
            invalidate_key('mainTable', key)
            cache.delete('ajaxlist:%s' % key)
            invalidate_key('search', key)
            cache.delete('ajaxsearch:%s' % key)
        cache.delete('Stat:1')
        super(AjaxTest, self).tearDown()

    def test_registration(self):
        a = api.Register()
        link = a.get_link()
        s = {}
        for key in a.params.keys():
            s[key] = 'a@a.aa'
        self.send_request(link, s, a.returns)
        self.send_request(link, {}, a.error)

    def test_login(self):
        from anime.tests._functions import user, email, passwd
        a = api.Login()
        link = a.get_link()
        s = {'username': user, 'password': passwd}
        self.send_request(link, s, a.returns)
        s['username'] = email
        self.send_request(link, s, a.error)
        self.client.logout()
        self.send_request(link, s, a.returns)

    @login()
    def test_add(self):
        a = api.Add()
        link = a.get_link()
        params = fill_params(a)
        self.send_request(link, params, a.returns)
        self.send_request(link, params, a.error)

    def test_search(self):
        a = api.Search()
        link = a.get_link()
        self.send_request(link, {'string': 'b', 'order': 'releasedAt', 'limit': 40, 'page': 1}, a.returns)
        self.send_request(link, {'string': 'b', 'order': 'releasedAt', 'limit': 40, 'page': 1}, a.returns)
        self.send_request(link, {'string': 'b', 'limit': 'd', 'page': 'f'}, a.error)
        self.send_request(link, {'string': 'b', 'fields': 'd,f'}, a.error)
        self.send_request(link, {'string': 'b', 'order': 'd'}, a.error)
        self.send_request(link, {}, a.error)

    def test_index(self):
        a = api.List()
        link = a.get_link()
        self.send_request(link, {}, a.returns)
        self.send_request(link, {'order': 'd'}, a.error)

    def test_get(self):
        a = api.Get()
        link = a.get_link()
        params = {'id': 1, 'field': ['name','title']}
        a.returns['text'].set_order(['name', 'title'])
        self.send_request(link, params, a.returns)

    @login()
    def test_forms(self):
        a = api.Forms()
        link = a.get_link()
        params = {'id': 1, 'model': 'anime', 'field': 'title'}
        self.send_request(link, params, a.get_returns('anime', 'title'))
        params = {'id': 1, 'model': 'anime', 'field': 'none'}
        self.send_request(link, params, a.error)

    @login()
    def test_set(self):
        a = api.Set()
        link = a.get_link()
        for name, model in EDIT_MODELS.items():
            if name == 'anime':
                for f in AnimeItem._meta.fields:
                    if not f.auto_created and f.name not in ['releasedKnown', 'endedKnown', 'bundle']:
                        params = fill_params(a.get_params(name, f.name),
                                    {'model': name, 'field': f.name})
                        self.send_request(link, params, a.get_returns(f.name))
                continue
            elif name in ['image', 'animerequest', 'request', 'feedback']:
                continue
            params = fill_params(a.get_params(name), {'model': name, 'field': None})
            self.send_request(link, params, a.get_returns(name))
        self.send_request(link, {}, a.error)

    def test_process_edit_response(self):
        from anime.views.ajax import process_edit_response
        self.assertEquals(process_edit_response({'form': None, 'status': True}),
            {'status': False, 'text': u'Form instance has bad type.',
             'response': 'error'})

    def test_filter(self):
        a = api.Filter()
        link = a.get_link()
        self.send_request(link, {'episodesCount_0': 25}, a.get_returns())
        self.send_request(link, {'episodesCount_0': 'u'}, a.error)
        self.send_request(link, {'releaseType': 1, 'genre': [2, 3],
        'state': 1, 'episodesCount_0': 25, 'episodesCount_2': True,
        'duration_0': 25, 'duration_1': '__gt', 'releasedAt_0': '2.02.2010'}, a.get_returns())
        self.client.get(reverse('index'))
        self.send_request(link, {}, a.get_returns())

    @login()
    def test_statistics(self):
        a = api.Statistics()
        link = a.get_link()
        self.send_request(link, {}, a.get_returns())
        self.client.logout()
        self.send_request(link, {'user_id': 1}, a.get_returns())
        self.send_request(link, {}, a.error)


class UserViewsTest(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    def tearDown(self):
        cache.delete('Stat:1')
        cache.delete('lastuserbundle:2')
        cache.delete('statusexportdata:1')
        cache.delete('userCss:1')
        key = '66811e1a68035d2514733b54be7e9fc7e98d5a2e',
        invalidate_key('mainTable', key)
        cache.delete('ajaxlist:%s' % key)
        super(UserViewsTest, self).tearDown()

    @login()
    def test_login_logout(self):
        from anime.tests._functions import user, passwd
        # logout
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, '/')
        # login
        response = self.client.post(reverse('login'), {'username': user, 'password': passwd})
        self.assertRedirects(response, '/')

    def test_social_error(self):
        self.assertEquals(self.client.get(reverse('social_error')).status_code, 200)

    def test_registration(self):
        response = self.client.post(reverse('registration'), {'register-email': 'u@uu.uu'})
        self.assertRedirects(response, '/')

    @login()
    def test_settings(self):
        self.assertEquals(self.client.get(reverse('settings')).status_code, 200)
        self.client.logout()
        self.assertEquals(self.client.get(reverse('settings')).status_code, 404)

    @login()
    def test_statistics(self):
        self.assertEquals(self.client.get(reverse('statistics')).status_code, 200)
        self.client.logout()
        self.assertEquals(self.client.get(reverse('statistics')).status_code, 404)
        self.assertEquals(self.client.get(reverse('statistics', args=[1])).status_code, 200)
        self.assertEquals(self.client.get(reverse('statistics', args=[2])).status_code, 404)

    @login()
    def test_css(self):
        self.assertEquals(self.client.get(reverse('user_css')).status_code, 200)

    @login()
    def test_statistics_export(self):
        self.assertEquals(self.client.get(reverse('statistics_export')).status_code, 200)
        self.client.logout()
        self.assertEquals(self.client.get(reverse('statistics_export')).status_code, 404)


class EditViewsTest(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    def tearDown(self):
        super(EditViewsTest, self).tearDown(self.fixtures + ['requests.json'])

    @login()
    def test_add(self):
        a = api.Add()
        self.assertEquals(self.client.get(reverse('edit_add')).status_code, 200)
        params = fill_params(a)
        count = last_record_pk(AnimeItem)
        response = self.client.post(reverse('edit_add'), params)
        self.assertRedirects(response, reverse('card', args=[count + 1]))

    @login()
    def test_edit(self):
        fields = api.Set()
        for name in ['bundle', 'state']:
            n = 0 if name == 'bundle' else 1
            params = fill_params(fields.get_params(name))
            if name == 'bundle':
                c = last_record_pk(AnimeBundle)
                rlink = reverse('edit_item', kwargs={'model': name, 'item_id': c + 1})
            else:
                rlink = reverse('card', args=[n])
            response = self.client.post(
                reverse('edit_item', kwargs={'model': name, 'item_id': n}), params)
            self.assertRedirects(response, rlink)
        # Test Image
        c = last_record_pk(AnimeRequest)
        with open(os.path.join(settings.MEDIA_ROOT, 'test', '1px.png'), 'r') as f:
            response = self.client.post(reverse('edit_item',
                    kwargs={'model': 'image', 'item_id': 1}), {'text': f})
        self.assertRedirects(response, reverse('request_item', args=[c + 1]))
        os.unlink(os.path.join(settings.MEDIA_ROOT, '1619e0741c0526b10c74eda382595812bd6679adf84.png'))


class EditViewsRequestsTest(TestCase):

    fixtures = ['requests.json']

    @create_user()
    def setUp(self):
        pass

    def tearDown(self):
        # FIXME: This string obtained by watching of cache calls.
        # TODO: Reverse this and make it dinamic
        for cname in ['e5cfc2c10ac18b2f0befdbb54f0e23247fdc333e',
                      'dfc48f25b896dd05ae8caed9f05280464100f0e3']:
            invalidate_key('requests', cname)
            cache.delete(cname)
        super(EditViewsRequestsTest, self).tearDown()

    @login()
    def test_requests_page(self):
        self.assertEquals(self.client.get(reverse('requests')).status_code, 200)
        self.assertEquals(self.client.get(reverse('requests',
                kwargs={'status': 1, 'rtype': 1, 'page': 1})).status_code, 200)
        self.assertEquals(self.client.get(reverse('requests', kwargs={
                            'status': 900})).status_code, 404)
        self.assertEquals(self.client.get(reverse('requests', kwargs={
                            'rtype': 900})).status_code, 404)

    @login()
    def test_requests(self):
        for i in range(0, 9):
            self.assertEquals(self.client.get(reverse('request_item', args=[i])).status_code, 200)

    @login()
    def test_new_requests(self):
        for link in (reverse('edit_feedback'), reverse('edit_animerequest')):
            self.assertEquals(self.client.get(link).status_code, 200)
            self.assertEquals(self.client.post(link, {}).status_code, 200)
            count = last_record_pk(AnimeRequest)
            response = self.client.post(link, {'text': 'new'})
            self.assertRedirects(response, reverse('request_item', args=[count + 1]))


class BaseViewsTest(TestCase):

    fixtures = ['2trash.json']

    def tearDown(self):
        cache.delete('card:1')
        cache.delete('card:2')
        super(BaseViewsTest, self).tearDown()

    def test_card(self):
        self.assertEquals(self.client.get(reverse('card'), follow=True).status_code, 200)
        self.assertEquals(self.client.get(reverse('card', args=[2])).status_code, 200)
        self.assertEquals(self.client.get(reverse('card', args=[300])).status_code, 404)


class BaseViewsNoFixturesTest(TestCase):

    def tearDown(self):
        #FIXME: what card?
        cache.delete('card:')
        super(BaseViewsNoFixturesTest, self).tearDown()

    def test_card(self):
        self.assertEquals(self.client.get(reverse('card'), follow=True).status_code, 200)


class ClassesViewsTest(TestCase):

    def tearDown(self):
        cache.delete(BLANK_CACHESTR)
        cache.delete('listtest:%s' % BLANK_CACHESTR)
        cache.delete('ajaxtest:%s' % BLANK_CACHESTR)
        super(ClassesViewsTest, self).tearDown(['2trash.json'])

    def blank(*args, **kwargs):
        return '', ''

    def test_AnimeListView(self):
        from anime.views.classes import AnimeListView
        v = AnimeListView()
        v.cache_name = 'listtest'
        v.request = fake_request()
        self.assertRaises(NotImplementedError, v.get_link)
        self.assertRaises(NotImplementedError, v.check_parameters, None)
        v.get_link = self.blank
        v.check_parameters = self.blank
        v.cache_name = ''
        self.assertEquals(v.get_context_data(object_list=None),
                {'list': None, 'link': '', 'pages': {}, 'cachestr': BLANK_CACHESTR})

    def test_AnimeAjaxListView(self):
        from anime.views.classes import AnimeAjaxListView
        v = AnimeAjaxListView()
        v.ajax_cache_name = 'ajaxtest'
        v.request = fake_request('')
        v.ajax_call = True
        self.assertRaises(NotImplementedError, v.post, None)
        v.cache_name = ''
        v.ajax_cache_name = ''
        cache.delete(':')
        self.assertEquals(v.updated(''), True)
        v.ajax_call = False
        v.get_link = self.blank
        v.check_parameters = self.blank
        self.assertEquals(v.get_context_data(object_list=None),
                {'list': None, 'head': None, 'link': '', 'pages': {},
                'cachestr': BLANK_CACHESTR})

    #~ def test_filter(self):
        #~ pass


class ListViewsTest(TestCase):

    fixtures = ['2trash.json']

    def tearDown(self):
        for cname in ['66811e1a68035d2514733b54be7e9fc7e98d5a2e',
                      '78a6a1ecae85ccea08dc9390082d2f570f743c9f',
                      '517cd1330ed1f76505e1f948bcb86557e4e9d451',
                      '8c78f52585d20cfc2eaca1329c371e8ea5782a3e']:
            invalidate_key('mainTable', cname)
            cache.delete('ajaxlist:%s' % cname)
        cache.delete('lastuserbundle:1')
        cache.delete('lastuserbundle:2')
        super(ListViewsTest, self).tearDown()

    @create_user()
    @create_user('2')
    @login()
    def test_IndexListView(self):
        self.assertEquals(self.client.get(reverse('index')).status_code, 200)
        self.assertEquals(self.client.get(reverse('index', kwargs={
                'status': 0, 'order': 'releasedAt'})).status_code, 200)
        self.assertEquals(self.client.get(reverse('index', kwargs={
                'user': 2, 'status': 1})).status_code, 200)
        self.assertEquals(self.client.get(reverse('index', kwargs={
                            'user': 3})).status_code, 404)
        self.assertEquals(self.client.get(reverse('index', kwargs={
                            'order': 'no'})).status_code, 404)
        self.client.logout()
        self.assertEquals(self.client.get(reverse('index', kwargs={
                            'status': 0})).status_code, 200)

    @create_user()
    def test_IndexListView_cache(self):
        cache.delete('userstatus:1:0')
        self.assertEquals(self.client.get(reverse('index', kwargs={
                'user': 1, 'status': 0})).status_code, 200)
        self.assertEquals(self.client.get(reverse('index', kwargs={
                'user': 1, 'status': 0})).status_code, 200)


class AjaxListViewsTest(TestCase):

    fixtures = ['2trash.json']

    def tearDown(self):
        # FIXME: key
        key = 'bf490f96cf04c4f95def45f7a693495665306345'
        invalidate_key('search', key)
        cache.delete('ajaxsearch:%s' % key)
        super(AjaxListViewsTest, self).tearDown()

    def test_SearchListView(self):
        from anime.views.ajaxlist import SearchListView
        s = SearchListView()
        s.kwargs = {}
        s.string = None
        s.order = u'title'
        s.page = 0
        s.fields = []
        self.assertEquals(unicode(s.get_queryset()), unicode(AnimeItem.objects.none()))
        self.assertEquals(s.get_link(), ({'link': '/search/'}, '/search/0'))
        request = fake_request('search', {'string': 'abcdef',
                'page': 1, 'fields': ['title'], 'limit': 5, 'order': 'title'})
        s.check_parameters(request)
        s.request = request
        #import pudb; pudb.set_trace()
        request_str = hexdigest('abcdef')
        self.assertEquals(s.get_link(), ({'link': '/search/abcdef/limit/5/',
            'limit': 5, 'string': u'abcdef'}, create_cachestr('search',
            link_data = {'string': request_str, 'limit': 5}, data=[u'title',])))
        self.assertEquals(unicode(s.get_queryset()), unicode(AnimeItem.objects.none()))
        self.assertEquals(self.client.get(reverse('search')).status_code, 200)
        invalidate_key('search', '/search/4a0a19218e082a343a1b17e5333409af9d98f0f5/sort/releasedAt/1')
        self.assertEquals(self.client.get(reverse('search', kwargs={
                'string': 'f', 'order': 'releasedAt'})).status_code, 200)
        cache.delete('ajaxsearch:/search/4a0a19218e082a343a1b17e5333409af9d98f0f5/sort/releasedAt/1')
        self.assertEquals(self.client.get(reverse('search', kwargs={
                'string': 'f', 'order': 'releasedAt'})).status_code, 200)
        self.assertEquals(self.client.get(reverse('search', kwargs={
                'string': 'f', 'order': 'releasedAt'})).status_code, 200)
        self.assertEquals(self.client.post(reverse('search', kwargs={
                'string': ' '})).status_code, 404)

    #~ def test_IndexListView(self):
        #~ pass





class HistoryViewsTest(TestCase):
    # Don't care about in this version

    fixtures = ['2trash.json']

    @create_user()
    @login()
    def test_add(self):
        from django.contrib.auth.models import User
        u = User.objects.get(id=1)
        u.is_staff = True
        u.save()
        self.assertEquals(self.client.get('/history/').status_code, 200)
        self.client.logout()
        self.assertEquals(self.client.get('/history/').status_code, 200)
