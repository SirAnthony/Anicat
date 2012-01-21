import datetime
import json
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.encoding import smart_unicode
from math import ceil
from random import randint

from anime import api
from anime.models import (AnimeItem, AnimeBundle, AnimeLink, Genre,
        UserStatusBundle, EDIT_MODELS, USER_STATUS, AnimeRequest,
        AnimeItemRequest, AnimeImageRequest, AnimeFeedbackRequest)
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

    def test_login(self):
        a = api.Login()
        link = a.get_link()
        s = {'username': 'nobody', 'password': 'qwerty'}
        self.send_request(link, s, a.returns)

    def test_search(self):
        a = api.Search()
        link = a.get_link()
        self.send_request(link, {'string': 'b', 'limit': 'd', 'page': 'f'}, a.returns)
        self.send_request(link, {'string': 'b', 'order': 'releasedAt', 'limit': 40, 'page': 2}, a.returns)

    @login()
    def test_add(self):
        a = api.Add()
        link = a.get_link()
        params = {'title': 12, 'releaseType': 6, 'episodesCount': 5, 'duration':  43,
                  'releasedAt': '2.4.1952', 'endedAt': '??.??.1952', 'air': True,
                  'genre': ('1','2'),}
        self.send_request(link, params, a.returns)

    @login()
    def test_get(self):
        a = api.Get()
        link = a.get_link()
        fields = [x.name for x in AnimeItem._meta.fields] + [
            'releasedAt,endedAt', 'release', 'type', 'genre', 'name', 'state', 'links']
        for i in [1, 2]:
            for f in fields:
                params = {'id': i, 'field': f}
                a.returns['text'].set_order([f])
                self.send_request(link, params, a.returns)

    @login()
    def test_forms(self):
        a = api.Forms()
        link = a.get_link()
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
