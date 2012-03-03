
from datetime import datetime
from django.core import mail

from anime.models import AnimeItem, Genre, AnimeRequest
from anime.tests._classes import CleanTestCase as TestCase
from anime.tests._functions import create_user
from anime.utils import cache, misc, paginator


class CacheTest(TestCase):

    def tearDown(self):
        cache.delete('1')
        cache.delete('AnimeItem')
        cache.delete('AnimeItem:1')
        cache.delete('a')
        cache.delete('b')
        cache.delete('Genre')
        cache.delete('Genre:1')
        super(TestCase, self).tearDown()

    def test_latest(self):
        self.assertEquals(cache.latest('IndexListView', '1'), False)
        self.assertEquals(cache.latest('IndexListView', '1'), False)

    def test_get_latest(self):
        self.assertRaisesMessage(ValueError,
                    cache.ERROR_MESSAGES['bad_item_type'].format(' '),
                    cache.get_latest, ' ')
        self.assertEquals(type(cache.get_latest('IndexListView')), datetime)
        self.assertEquals(type(cache.get_latest('IndexListView',
                    {'AnimeItem': [1, 2]})), datetime)

    def test_get_cache_name(self):
        g = Genre(name='1')
        g.save()
        self.assertEquals(cache.get_cache_name(Genre, [1, 1]),
                            ['Genre:1', 'Genre:1'])
        self.assertEquals(cache.get_cache_name(g), 'Genre:1')
        self.assertEquals(cache.get_cache_name(Genre), 'Genre')

    def test_get_named_cache(self):
        name = 'a'
        names_list = ['a', 'b']
        date = cache.update_named_cache(name)
        self.assertEquals(cache.get_named_cache(name), date)
        dates = cache.update_named_cache(names_list)
        self.assertEquals(cache.get_named_cache(names_list),
                            {'a': dates, 'b': dates})
        cache.delete('a')
        cache.delete('b')

    def test_update_named_cache(self):
        name = 'a'
        names_list = ['a', 'b']
        self.assertEquals(type(cache.update_named_cache(name)), datetime)
        self.assertEquals(type(cache.update_named_cache(names_list)), datetime)

    def test_update_cache(self):
        name = 'a'
        self.assertEquals(type(cache.update_cache(Genre)), datetime)

    def test_update_cache_on_save(self):
        g = Genre(name='1')
        g.save()
        cache.update_cache_on_save(None, g, None)

    def test_key_valid_invalidate(self):
        from django.utils.hashcompat import md5_constructor
        from django.utils.http import urlquote
        fragment_name = 'a'
        variables = ['a']
        args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
        cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
        cache.cset(cache_key, True)
        self.assertEquals(cache.key_valid(fragment_name, *variables), True)
        cache.invalidate_key(fragment_name, *variables)
        self.assertEquals(cache.key_valid(fragment_name, *variables), False)
        cache.cset(cache_key, True)
        cache.clean_cache(fragment_name, *variables)
        self.assertEquals(cache.key_valid(fragment_name, *variables), False)


class CatalogTest(TestCase):

    fixtures = ['2trash.json']

    def test_last_record_pk(self):
        from anime.utils import catalog
        self.assertEquals(catalog.last_record_pk(AnimeItem),
                AnimeItem.objects.order_by('-pk')[0].pk)
        self.assertEquals(catalog.last_record_pk(AnimeRequest), 0)


class ConfitTest(TestCase):

    #lol, why?
    def test_random_string(self):
        from anime.utils import config
        reload(config)
        self.assertEquals(type(config.random_string()), unicode)


class MiscTest(TestCase):

    def test_is_iterator(self):
        from itertools import chain
        for item in (list(), tuple(), chain()):
            self.assertEquals(misc.is_iterator(item), True)
        self.assertEquals(misc.is_iterator(True), False)

    def test_safe_username(self):
        self.assertEquals(misc.safe_username('a@a.a'), 'a')

    def test_username_for_email(self):
        self.assertEquals(misc.username_for_email('a@a.a'), 'a-d656370')

    @create_user()
    def test_new_user(self):
        from django.contrib.auth.models import User
        u = User.objects.get(id=1)
        self.assertEquals(misc.new_user(None, u, None, None), True)
        self.assertEquals(mail.outbox[0].to, [u.email])

    def test_generate_password(self):
        self.assertEquals(type(misc.generate_password()), unicode)

    def test_mail(self):
        misc.mail('a@aa.aa', {'username': 'a', 'password': 'a',
            'openid': True}, 'anime/user/welcome.txt',
            'anime/user/registred_email.html')
        self.assertEquals(mail.outbox[0].to, ['a@aa.aa'])


class PaginatorTest(TestCase):

    fixtures = ['2trash.json']

    pg = paginator.Paginator(AnimeItem.objects.all(), 1)

    def tearDown(self):
        cache.delete('Pages:c')
        super(TestCase, self).tearDown()

    def test_name_length(self):
        self.assertEquals(self.pg.name_length, 4)

    def test_set_order_cachestr(self):
        self.pg.set_order('id')
        self.assertEquals((self.pg.order, self.pg.reverse), ('id', '-'))
        self.pg.set_order('-id')
        self.assertEquals((self.pg.order, self.pg.reverse), ('id', ''))
        self.pg.set_cachekey('c')
        self.assertEquals(self.pg.cachekey, 'c')

    def test_get_names(self):
        self.pg.set_order('-id')
        self.pg.set_cachekey('c')
        self.assertEquals(self.pg.get_names(), [u'2 - 2', u'1 - 1'])

    def test_iternames(self):
        # Exception raising only
        self.pg.object_list = None
        self.pg.set_order('id')
        self.assertRaises(TypeError, self.pg.iternames().next)
