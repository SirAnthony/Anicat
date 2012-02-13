
import json

from django.test import TestCase

from anime import api
from anime.models import AnimeItem, EDIT_MODELS
from anime.tests.functions import create_user, login, check_response, fill_params



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

