
from django.test import TestCase
from django.core.cache import cache
from anime.tests._functions import check_response


FIXTURES_MAP = {
    '2trash.json': {
        'AnimeBundle': 3, 'AnimeItem': 2, 'AnimeName': 8, 'AnimeLink': 3
    },
    'requests.json': {
        'AnimeRequest': 86
    },
}


class CleanTestCase(TestCase):

    def tearDown(self):
        for fixture in getattr(self, 'fixtures', []):
            for k, v in FIXTURES_MAP[fixture].items():
                for i in range(1, v+1):
                    cache.delete('{0}:{1}'.format(k, v))
                cache.delete(k)

    def check_response(self, ret, returns):
        try:
            check_response(ret, returns)
        except AssertionError, e:
            raise AssertionError('Error in response check. Data: %s, %s\nOriginal message: %s' % (
                    ret, returns, e.message))
