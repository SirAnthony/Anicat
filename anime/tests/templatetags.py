from anime.templatetags import animefilters
from django.test import TestCase

class AnimeFiltersTests(TestCase):

    def test_hash(self):
        self.assertEquals(animefilters.hash({1: True}, True), True)
