import datetime
import json
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.encoding import smart_unicode

import api
from anime.models import AnimeItem, AnimeBundle, AnimeLink, Genre, EDIT_MODELS, USER_STATUS
from anime.forms.json import is_iterator

user = 'nobody'
email = 'nobody@example.com'
passwd = 'querty'

def login(u=None, pwd=None):
    def wrap(f):
        def d_login(self, *args, **kwargs):
            params = {'username': u or user, 'password': pwd or passwd}
            self.assertEquals(self.client.post('/login/', params).status_code, 302)
            f(self, *args, **kwargs)
        return d_login
    return wrap

def create_user(u=None, e=None, p=None, lng=False):
    def wrap(f):
        def d_create(self, *args, **kwargs):
            us = User.objects.create_user(u or user, e or email, p or passwd)
            us.date_joined = datetime.date.today() - datetime.timedelta(20)
            us.save()
            f(self, *args, **kwargs)
        return d_create
    return wrap

def check_response(response, origin, *args, **kwargs):

    if origin is None:
        raise AssertionError('Original is None: %s' % origin)

    if isinstance(origin, dict):
        if not isinstance(response, dict):
            raise AssertionError('%s not match original type: %s' % (response, origin))
        #elif not isinstance(origin, api.NoneableDict) and \
        #        len(origin.keys()) != len(response.keys()):
        #    raise AssertionError('%s fields count differs from %s' % (response, origin))
        else:
            for key, item in origin.items():
                try:
                    check_response(response[key], item, *args, **kwargs)
                except KeyError:
                    # Field may be absent if value is None
                    if item is not None and not isinstance(origin, api.NoneableDict) and \
                       not isinstance(item, api.Noneable):
                        raise AssertionError('%s not match original: %s;\nKey: %s, item: %s' % (response, origin, key, item))
            return

    if isinstance(origin, basestring):
        if not isinstance(response, basestring):
            raise AssertionError('%s is not string. Type does not match: %s' % (response, origin))
        elif not origin == response:
            raise AssertionError('%s not match original: %s' % (response, origin))
        return

    if is_iterator(origin):
        if not is_iterator(response):
            raise AssertionError('%s not match original type: %s' % (response, origin))
        if isinstance(origin, api.FuzzyList):
            origin.set_count(len(response))
        for i in range(0, len(origin)):
            try:
                check_response(response[i], origin[i], *args, **kwargs)
            except IndexError:
                raise AssertionError('%s not match original: %s. Item %s not found' % (response, origin, origin[i]))
            except Exception, e:
                raise e
        return

    if isinstance(origin, bool):
        if not isinstance(response, bool):
            raise AssertionError('%s not match original type: %s' % (response, origin))
        else:
            if not response == origin:
                raise AssertionError('%s not match original: %s' % (response, origin))
        return

    if isinstance(origin, api.Noneable):
        if response is not None:
           check_response(response, origin.type)
        return

    if isinstance(origin, type):
        if not type(response) == origin:
            if origin is datetime.date and type(response) is unicode: #rewrite
                return
            if origin != unicode or type(response) not in (str, bool, int, float, long, complex):
                raise AssertionError('%s type (%s) not match original type: %s' % (response, type(response), origin))
        return

    if callable(origin):
        check_response(response, origin(*args, **kwargs), *args, **kwargs) #le fu


class NormalTest(TestCase):

    @create_user()
    def setUp(self):
        pass

    def test_registration(self):
        params = {}
        register_link = '/register/'
        #First try bad attempts
        for param, value in (('register-username', 'u'), ('register-email', 'u@uu.uu'),
                             ('register-password1', 'u')):
            params[param] = value
            response = self.client.post(register_link, params)
            self.assertEquals(response.status_code, 200)
        #Next try real register
        params["register-password2"] = 'u'
        response = self.client.post(register_link, params)
        self.assertEquals(response.status_code, 302)
        self.assert_(response["Location"].endswith('/'))

    @login()
    def test_login_logout(self):
        # logout
        response = self.client.get('/logout/')
        self.assertEquals(response.status_code, 302)
        self.assert_(response["Location"].endswith('/'))
        #bad login
        response = self.client.post('/login/', {})
        self.assertEquals(response.status_code, 200)

    @login()
    def test_add(self):
        Genre(name='1').save()
        Genre(name='2').save()
        add_link = '/add/'
        params = {'title': 12, 'releaseType': 6, 'episodesCount': 5, 'duration':  43,
                  'releasedAt': '2.4.1952', 'endedAt': '??.??.1952', 'air': True,
                  'genre': ('1','2'),}
        #test blank input
        response = self.client.post(add_link, params)
        self.assertEquals(response.status_code, 302)

    @login()
    def test_forms(self):
        link = '/edit/%s/%d/'
        AnimeItem(title=123, releaseType=6, episodesCount=5, duration=43,
                releasedAt=datetime.date.today(), air=True).save()
        for name, model in EDIT_MODELS.items():
            n = 0
            if name in ['name', 'links', 'state', 'image']:
                n = 1
            self.assertEquals(self.client.get(link % (name, n), {}).status_code, 200)

    @login()
    def test_fields(self):
        link = '/edit/anime/0/%s/'
        for f in AnimeItem._meta.fields:
            if not f.auto_created and f.name not in ['releasedKnown', 'endedKnown', 'bundle']:
                self.assertEquals(self.client.get(link % f.name, {}).status_code, 200)
        self.assertEquals(self.client.get(link % 'genre', {}).status_code, 200)


class AjaxTest(TestCase):

    def send_request(self, link, params, returns):
        response = self.client.post(link, params)
        ret = json.loads(response._container[0])
        try:
            check_response(ret, returns)
        except AssertionError, e:
            raise AssertionError('Error in response check. Data: %s, %s\nOriginal message: %s' % (
                    ret, returns, e.message))

    def test_registration(self):
        a = api.Register()
        link = a.get_link()
        s = {}
        for key in a.params.keys():
            s[key] = 'a@a.aa'
        self.send_request(link, s, a.returns)

    @create_user()
    def test_login(self):
        a = api.Login()
        link = a.get_link()
        s = {'username': 'nobody', 'password': 'querty'}
        self.send_request(link, s, a.returns)

    @create_user()
    @login()
    def test_add(self):
        a = api.Add()
        Genre(name='1').save()
        Genre(name='2').save()
        link = a.get_link()
        params = {'title': 12, 'releaseType': 6, 'episodesCount': 5, 'duration':  43,
                  'releasedAt': '2.4.1952', 'endedAt': '??.??.1952', 'air': True,
                  'genre': ('1','2'),}
        self.send_request(link, params, a.returns)

    @create_user()
    @login()
    def test_get(self):
        a = api.Get()
        link = a.get_link()
        anime = AnimeItem(title=123, releaseType=6, episodesCount=5, duration=43,
                    releasedAt=datetime.date.today(),
                    endedAt=datetime.date.today(), air=True)
        AnimeBundle.tie(anime,
            AnimeItem(title=1234, releaseType=6, episodesCount=5, duration=43,
                        releasedAt=datetime.date.today(), air=False)
        )
        AnimeLink(anime=anime, link="http://example.org", linkType=1).save()
        AnimeLink(anime=anime, link="http://example.com", linkType=1).save()
        AnimeLink(anime=anime, link="http://www.example.org", linkType=2).save()
        fields = [x.name for x in AnimeItem._meta.fields] + [
            'releasedAt,endedAt', 'release', 'type', 'genre', 'name', 'state', 'links']
        for i in [1, 2]:
            for f in fields:
                params = {'id': i, 'field': f}
                a.returns['text'].set_order([f])
                self.send_request(link, params, a.returns)

    def test_search(self):
        a = api.Search()
        link = a.get_link()
        for i in range(0, 40):
            AnimeItem(title='test%d' % i, releaseType=1, episodesCount=5, duration=43,
                    releasedAt=datetime.date.today(), endedAt=datetime.date.today(), air=True).save()
        self.send_request(link, {'string': 'test', 'limit': 'd', 'page': 'f'}, a.returns)
        self.send_request(link, {'string': 't', 'order': 'releasedAt', 'limit': 40, 'page': 2}, a.returns)

    @create_user()
    @login()
    def test_forms(self):
        a = api.Forms()
        link = a.get_link()
        anime = AnimeItem(title=123, releaseType=6, episodesCount=5, duration=43,
                releasedAt=datetime.date.today(), air=True)
        AnimeBundle.tie(anime,
            AnimeItem(title=1234, releaseType=6, episodesCount=5, duration=43,
                        releasedAt=datetime.date.today(), air=False)
        )
        AnimeLink(anime=anime, link="http://example.org", linkType=1).save()
        AnimeLink(anime=anime, link="http://example.com", linkType=2).save()
        for name, model in EDIT_MODELS.items():
            params = {'id': 1, 'model': name}
            if name == 'anime':
                for f in AnimeItem._meta.fields:
                    if not f.auto_created and f.name not in ['releasedKnown', 'endedKnown', 'bundle']:
                        params['field'] = f.name
                        self.send_request(link, params, a.get_returns(name, f.name))
                del params['field']
                continue
            self.send_request(link, params, a.get_returns(name))

    def fill_params(self, sample, data={}):

        for t in (basestring, str, bool, int, float, long, complex, type(None)):
            if isinstance(sample, t):
                return sample

        if isinstance(sample, api.Noneable):
            t = sample.default if sample.default is not None else sample.type
            return self.fill_params(t)

        if isinstance(sample, dict):
            params = {}
            for key, value in sample.iteritems():
                param = self.fill_params(data[key] if key in data else value)
                if param is not None:
                    params[key] = param
            #print params
            return params

        if is_iterator(sample):
            return [self.fill_params(s) for s in sample]

        if isinstance(sample, type):
            if sample in (unicode, str):
                return u'a'
            elif sample is int:
                return 1
            elif sample is datetime.date:
                return datetime.date.today()
            else:
                raise TypeError('Not supported type: {0}'.format(sample))

    @create_user()
    @login()
    def test_set(self):
        a = api.Set()
        link = a.get_link()
        AnimeItem(title='123', releaseType=6, episodesCount=5, duration=43,
                releasedAt=datetime.date.today(), air=True).save()
        AnimeItem(title='1234', releaseType=6, episodesCount=5, duration=43,
                        releasedAt=datetime.date.today(), air=False).save()
        for name, model in EDIT_MODELS.items():
            if name == 'anime':
                for f in AnimeItem._meta.fields:
                    if not f.auto_created and f.name not in ['releasedKnown', 'endedKnown', 'bundle']:
                        params = self.fill_params(
                                    a.get_params(name, f.name),
                                    {'model': name, 'field': f.name})
                        self.send_request(link, params, a.get_returns(f.name))
                continue
            elif name in ['image', 'animerequest', 'request', 'feedback']:
                continue
            params = self.fill_params(a.get_params(name), {
                                    'model': name, 'field': None})
            self.send_request(link, params, a.get_returns(name))
