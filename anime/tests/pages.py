import datetime
import json
import os
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, client
from django.utils.encoding import smart_unicode
from django.utils.unittest import skip
from math import ceil
from random import randint

from anime import api
from anime.models import (AnimeItem, AnimeBundle, AnimeLink, Genre,
        UserStatusBundle, EDIT_MODELS, USER_STATUS, AnimeRequest,
        AnimeItemRequest, AnimeImageRequest, AnimeFeedbackRequest)
from anime.tests.functions import create_user, login, fill_params


class NoDBTests(TestCase):

    def test_registration(self):
        params = {}
        register_link = '/register/'
        #First try bad attempts
        response = self.client.post(register_link, {'register-email': 'u@uu.uu'})
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
        count = AnimeItem.objects.count()
        response = self.client.post(add_link, params)
        self.assertRedirects(response, '/card/{0}/'.format(count + 1))

    @login()
    def test_forms(self):
        link = '/edit/{0}/{1}/'
        fields = api.Set()
        for name in EDIT_MODELS.keys():
            if name in ('anime', 'image', 'request', 'feedback', 'animerequest'):
                # test_fields and test_image functions and RequestsTest case
                continue
            n = 0 if name == 'bundle' else 1
            params = fill_params(fields.get_params(name))
            rlink = '/card/{0}/'
            c = 0
            if name == 'bundle':
                c = AnimeBundle.objects.count()
                rlink = '/edit/bundle/{0}/'
            elif name == 'anime':
                c = AnimeItem.objects.count()
            response = self.client.post(link.format(name, n), params)
            self.assertRedirects(response, rlink.format(c + 1))

    @login()
    def test_image(self):
        files = ['test_random.jpg', ]
        c = AnimeRequest.objects.count()
        with open(os.path.join(settings.MEDIA_ROOT, 'test', '1px.png'), 'r') as f:
            response = self.client.post('/edit/image/1/', {'text': f})
        self.assertRedirects(response, '/request/{0}/'.format(c + 1))
        os.unlink(os.path.join(settings.MEDIA_ROOT, '1619e0741c0526b10c74eda382595812bd6679adf84.png'))

    @login()
    def test_fields(self):
        link = '/edit/anime/0/%s/'
        for f in AnimeItem._meta.fields:
            if not f.auto_created and f.name not in ['releasedKnown', 'endedKnown', 'bundle']:
                self.assertEquals(self.client.get(link % f.name, {}).status_code, 200)
        self.assertEquals(self.client.get(link % 'genre', {}).status_code, 200)

    def test_card(self):
        self.assertEquals(self.client.get('/card/', follow=True).status_code, 200)
        self.assertEquals(self.client.get('/card/2/').status_code, 200)
        self.assertEquals(self.client.get('/card/300/').status_code, 200)

    @login()
    def test_state(self):
        self.assertEquals(self.client.get('/css/').status_code, 200)
        self.assertEquals(self.client.get('/stat/').status_code, 200)
        self.assertEquals(self.client.get('/stat/6/').status_code, 200)

    def test_search(self):
        self.assertEquals(self.client.get('/search/1/').status_code, 200)

    def test_history(self):
        self.assertEquals(self.client.get('/history/add/').status_code, 200)


#@skip
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
        self.assertEquals(self.client.get('/requests/status/1/type/1/').status_code, 200)

    @login()
    def test_user_requests(self):
        self.assertEquals(self.client.get('/settings/').status_code, 200)

    @login()
    def test_requests(self):
        for i in range(0, 9):
            self.assertEquals(self.client.get('/request/{0}/'.format(i)).status_code, 200)

    @login()
    def test_new_requests(self):
        for link in ('/feedback/', '/animerequest/'):
            self.assertEquals(self.client.get(link).status_code, 200)
            self.assertEquals(self.client.post(link, {}).status_code, 200)
            count = AnimeRequest.objects.count()
            response = self.client.post(link, {'text': 'new'})
            self.assertRedirects(response, '/request/{0}/'.format(count + 1))


class ErrorTest(TestCase):

    @create_user()
    def setUp(self):
        pass

    @login()
    def test_add(self):
        add_link = '/add/'
        self.assertEquals(self.client.post(add_link, {}).status_code, 200)

    @login()
    def test_forms(self):
        link = '/edit/%s/%d/'
        for name, model in EDIT_MODELS.items():
            n = 0
            if name in ['name', 'links', 'state', 'image']:
                n = 1
            self.assertEquals(self.client.get(link % (name, n), {}).status_code, 200)
