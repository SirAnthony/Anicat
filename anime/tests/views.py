
import json
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from anime import api
from anime.models import AnimeItem, AnimeBundle, AnimeRequest, EDIT_MODELS
from anime.tests.functions import create_user, login, check_response, fill_params, last_record



class AjaxTest(TestCase):

    fixtures = ['2trash.json']

    def send_request(self, link, params, returns):
        response = self.client.post(link, params)
        ret = json.loads(response._container[0])
        try:
            check_response(ret, returns)
        except AssertionError, e:
            raise AssertionError('Error in response check. Data: %s, %s\nOriginal message: %s' % (
                    ret, returns, e.message))

    @create_user()
    def setUp(self):
        pass

    def test_registration(self):
        a = api.Register()
        link = a.get_link()
        s = {}
        for key in a.params.keys():
            s[key] = 'a@a.aa'
        self.send_request(link, s, a.returns)
        self.send_request(link, {}, a.error)

    def test_login(self):
        from anime.tests.functions import user, email, passwd
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
        self.send_request(link, {'string': 'b', 'limit': 'd', 'page': 'f'}, a.returns)
        self.send_request(link, {'string': 'b', 'order': 'releasedAt', 'limit': 40, 'page': 2}, a.returns)
        response = self.client.get(link, {})
        self.assertEquals(json.loads(response._container[0]),
            {u'text': {u'__all__': u'Only POST method allowed.'},
             u'response': u'error'})

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
        self.assertEquals(process_edit_response({'form': None}),
            {'status': False, 'text': u'Form instance has bad type.',
             'response': 'error'})


class UserViewsTest(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    @login()
    def test_login_logout(self):
        from anime.tests.functions import user, passwd
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


class EditViewsTest(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    @login()
    def test_add(self):
        a = api.Add()
        self.assertEquals(self.client.get(reverse('edit_add')).status_code, 200)
        params = fill_params(a)
        count = last_record(AnimeItem)
        response = self.client.post(reverse('edit_add'), params)
        self.assertRedirects(response, reverse('card', args=[count + 1]))

    @login()
    def test_edit(self):
        fields = api.Set()
        for name in ['bundle', 'state']:
            n = 0 if name == 'bundle' else 1
            params = fill_params(fields.get_params(name))
            if name == 'bundle':
                c = last_record(AnimeBundle)
                rlink = reverse('edit_item', kwargs={'model': name, 'item_id': c + 1})
            else:
                rlink = reverse('card', args=[n])
            response = self.client.post(
                reverse('edit_item', kwargs={'model': name, 'item_id': n}), params)
            self.assertRedirects(response, rlink)
        # Test Image
        c = last_record(AnimeRequest)
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

    @login()
    def test_requests_page(self):
        self.assertEquals(self.client.get(reverse('requests')).status_code, 200)
        self.assertEquals(self.client.get(reverse('requests',
                    kwargs={'status': 1, 'rtype': 1})).status_code, 200)

    @login()
    def test_requests(self):
        for i in range(0, 9):
            self.assertEquals(self.client.get(reverse('request_item', args=[i])).status_code, 200)

    @login()
    def test_new_requests(self):
        for link in (reverse('edit_feedback'), reverse('edit_animerequest')):
            self.assertEquals(self.client.get(link).status_code, 200)
            self.assertEquals(self.client.post(link, {}).status_code, 200)
            count = last_record(AnimeRequest)
            response = self.client.post(link, {'text': 'new'})
            self.assertRedirects(response, reverse('request_item', args=[count + 1]))

