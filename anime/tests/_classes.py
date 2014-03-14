
from django.test import TestCase
from django_nose import FastFixtureTestCase
from anime.tests._functions import check_response
from anime.utils import cache
from anime.utils.cache import invalidate_key


FIXTURES_MAP = {
    '2trash.json': {
        'AnimeBundle': 3, 'AnimeItem': 2, 'AnimeName': 9, 'AnimeLink': 3,
        'UserStatusBundle': 2
    },
    'requests.json': {
        'AnimeRequest': 86
    },
    '100trash.json': {
        'AnimeBundle': 100, 'AnimeItem': 110, 'AnimeName': 1000, 'AnimeLink': 1000,
        'UserStatusBundle': 1000
    },
}

class CleanTest(object):

    def tearDown(self, fixture_names=[]):
        fixtures = fixture_names or getattr(self, 'fixtures', [])
        for fixture in fixtures:
            for k, v in FIXTURES_MAP[fixture].items():
                for i in range(1, v+1):
                    cache.delete('{0}:{1}'.format(k, i))
                cache.delete(k)
        caches = getattr(self, 'caches', None)
        if caches:
            for key in caches:
                invalidate_key('mainTable', key)
                invalidate_key('search', key)
                invalidate_key('requests', key)
                cache.delete('ajaxlist:%s' % key)
                cache.delete('ajaxsearch:%s' % key)
                cache.delete('Pages:%s' % key)
                cache.delete(key)
        invalidate_key('footer', True)
        invalidate_key('footer', False)
        session = self.client.session.get('session_key')
        invalidate_key('filter', session)

    def check_response(self, ret, returns):
        try:
            check_response(ret, returns)
        except AssertionError, e:
            raise AssertionError('Error in response check. Data: %s, %s\nOriginal message: %s' % (
                    ret, returns, e))


class FastFixtureCase(CleanTest, FastFixtureTestCase):
    def tearDown(self, fixture_names=[]):
        CleanTest.tearDown(self, fixture_names)
        FastFixtureTestCase.tearDown(self)

class CleanTestCase(CleanTest, TestCase):
    def tearDown(self, fixture_names=[]):
        CleanTest.tearDown(self, fixture_names)
        TestCase.tearDown(self)
