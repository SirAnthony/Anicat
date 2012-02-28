
from django.test import TestCase
from anime import models



class ModelsTest(TestCase):


    def test_Genre(self):
        g = models.Genre(name='a')
        self.assertEquals(unicode(g), u'a')

    def test_Credit(self):
        c = models.Credit(title='a')
        self.assertEquals(unicode(c), u'a')


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


