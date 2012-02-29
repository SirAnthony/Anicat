
from django.contrib.auth.models import User
from django.test import TestCase
from anime import models



class ModelsTest(TestCase):


    def test_Genre(self):
        g = models.Genre(name='a')
        self.assertEquals(unicode(g), u'a')

    def test_Credit(self):
        c = models.Credit(title='a')
        self.assertEquals(unicode(c), u'a')

    def test_AnimeEpisode(self):
        c = models.AnimeEpisode(title='a', anime=models.AnimeItem(title='a'))
        self.assertEquals(unicode(c), u'a [a]')

    def test_AnimeName(self):
        c = models.AnimeName(title='a', anime=models.AnimeItem(title='a'))
        self.assertEquals(unicode(c), u'a')

    def test_Organisation_People(self):
        for m in [models.Organisation, models.People]:
            i = m(name='a')
            self.assertEquals(unicode(i), u'a')


class ModelsFixturesTest(TestCase):

    fixtures = ['2trash.json']

    def test_AnimeBundle(self):
        # Test save
        b = models.AnimeBundle()
        setattr(b, 'Bundle 0', 1)
        self.assertRaises(ValueError, b.save)
        b = models.AnimeBundle()
        a1 = models.AnimeItem.objects.get(id=1)
        a2 = models.AnimeItem.objects.get(id=2)
        setattr(b, 'Bundle 0', a1)
        setattr(b, 'Bundle 1', a2)
        b.save()
        self.assertEquals(a1.bundle, a2.bundle)
        setattr(b, 'Bundle 0', a1)
        b.save()
        # We need to reload objects
        a1 = models.AnimeItem.objects.get(id=1)
        a2 = models.AnimeItem.objects.get(id=2)
        self.assertEquals((a1.bundle, a2.bundle), (None, None))
        # Test tie
        self.assertRaises(ValueError, models.AnimeBundle.tie, None, None)
        models.AnimeBundle.tie(a1, a2)
        self.assertEquals(a1.bundle, a2.bundle)
        # Test untie
        self.assertEquals(a1.bundle.untie(None), None)
        a1.bundle.untie(a2)
        self.assertEquals(a2.bundle, None)

    def test_AnimeItem(self):
        from datetime import datetime
        a = models.AnimeItem(releasedAt=datetime.now(),
            episodesCount=230, title='d', releasedKnown=0,
            releaseType=5, endedKnown=0, duration=17)
        self.assertEquals(unicode(a), '')
        a.save()
        self.assertEquals(unicode(a), 'd [ONA]')
        self.assertEquals(a.release, '29.02.2012')
        self.assertEquals(a.releaseTypeS, 'ONA')
        a.title = 'd1'
        a.endedAt = datetime.now()
        models.AnimeName(anime=a, title='d1').save()
        a.save()
        self.assertEquals(a.release, '29.02.2012 - 29.02.2012')
        a.releasedKnown = 55
        self.assertEquals(a.release, 'Bad value')

    def test_AnimeLink(self):
        l = models.AnimeLink.objects.get(id=1)
        l.linkType = 0
        l.save()
        self.assertEquals(l.linkType, models.LINKS_TYPES[-1][0])

    def test_UserStatusBundle(self):
        ub = models.UserStatusBundle.objects.get(id=1)
        ub.state = 1
        ub.save()
        self.assertEquals(ub.count, None)
        ub.state = 2
        ub.save()
        self.assertEquals(ub.count, 1)
        ub.count = -1
        ub.save()
        self.assertEquals(ub.count, 1)
        ub.count = 999999
        ub.save()
        self.assertEquals(ub.count, ub.anime.episodesCount)

