
from django.test import TestCase
from anime.tests._functions import check_response
from anime.utils import cache


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


class CleanTestCase(TestCase):

    def tearDown(self, fixture_names=[]):
        fixtures = fixture_names or getattr(self, 'fixtures', [])
        for fixture in fixtures:
            for k, v in FIXTURES_MAP[fixture].items():
                for i in range(1, v+1):
                    cache.delete('{0}:{1}'.format(k, i))
                cache.delete(k)

    def check_response(self, ret, returns):
        try:
            check_response(ret, returns)
        except AssertionError, e:
            raise AssertionError('Error in response check. Data: %s, %s\nOriginal message: %s' % (
                    ret, returns, e.message))
