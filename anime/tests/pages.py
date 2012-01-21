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
from anime.tests.functions import create_user, login

class NoDBTests(TestCase):

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
        self.assertRedirects(response, '/')

    @create_user()
    @login()
    def test_login_logout(self):
        # logout
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/')
        #bad login
        response = self.client.get('/login/')
        self.assertEquals(response.status_code, 200)


class NormalTest(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    @login()
    def test_add(self):
        add_link = '/add/'
        params = {'title': 12, 'releaseType': 6, 'episodesCount': 5, 'duration':  43,
                  'releasedAt': '2.4.1952', 'endedAt': '??.??.1952', 'air': True,
                  'genre': ('1','2'),}
        #test blank input
        count = AnimeItem.objects.count()
        response = self.client.post(add_link, params)
        self.assertRedirects(response, '/card/{0}/'.format(count + 1))

    @login()
    def test_forms(self):
        link = '/edit/%s/%d/'
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

    def test_card(self):
        #self.assertEquals(self.client.get('/card/').status_code, 302)
        self.assertEquals(self.client.get('/card/2/').status_code, 200)

    @login()
    def test_state(self):
        self.assertEquals(self.client.get('/css/').status_code, 200)
        self.assertEquals(self.client.get('/stat/').status_code, 200)


class BigTest(TestCase):

    fixtures = ['100trash.json']

    @create_user()
    def setUp(self):
        pass

    @create_user('1')
    @create_user('2')
    def test_index(self):
        self.assertEquals(self.client.get('/').status_code, 200)
        for us in User.objects.all():
            for status in USER_STATUS:
                scount = UserStatusBundle.objects.filter(user=us, state=status[0]).count()
                if not scount:
                    continue
                for field in AnimeItem._meta.fields:
                    for o in ['', '-']:
                        for page in range(0, int(ceil(float(scount)/settings.INDEX_PAGE_LIMIT))):
                            link = '/user/{0}/show/{1}/sort/{2}{3}/{4}/'.format(us.id, status[0], o, field.name, page)
                            self.assertEquals(self.client.get(link).status_code, 200)

class RequestsTest(TestCase):

    fixtures = ['requests.json']

    @create_user()
    def setUp(self):
        pass

    @login()
    def test_requests_page(self):
        self.assertEquals(self.client.get('/requests/').status_code, 200)

    @login()
    def test_user_requests(self):
        self.assertEquals(self.client.get('/settings/').status_code, 200)
