
import anime.core.user as userMethods
import anime.core.base as coreMethods
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpRequest

from anime import api
from anime.core import explorer
from anime.forms.json import FormSerializer as FS
from anime.models import AnimeItem
from anime.tests._classes import CleanTestCase as TestCase
from anime.tests._functions import create_user, login, check_response


class UserTest(TestCase):

    @create_user()
    def setUp(self):
        pass

    def tearDown(self):
        cache.delete('MalList:1')
        super(TestCase, self).tearDown()

    def test_get_username(self):
        u = User.objects.get(id=1)
        self.assertEquals(userMethods.get_username(None), 'Anonymous')
        self.assertEquals(userMethods.get_username(u), 'Anonymous')
        u.first_name = 1
        u.save()
        self.assertEquals(userMethods.get_username(u), u.first_name)
        u.last_name = 2
        u.save()
        self.assertEquals(userMethods.get_username(u),
            '{0} {1}'.format(u.first_name, u.last_name))

    def test_login(self):
        from anime.tests._functions import user, passwd
        from anime.forms.User import NotActiveAuthenticationForm as Form
        r = HttpRequest()
        r.user = u = User.objects.get(id=1)
        self.assertEquals(userMethods.login(r),
            {'text': userMethods.ERROR_MESSAGES['login']['logined']})
        r.user = AnonymousUser()
        result = userMethods.login(r)
        result['form'] = FS(result['form'])
        self.assertEquals(result, {'form': FS(Form())})
        r.POST = {'username': user, 'password': passwd}
        engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        r.session = engine.SessionStore("New")
        self.assertEquals(userMethods.login(r), {'text':
                            {'name': 'Anonymous'}, 'response': True})

    def test_register(self):
        from anime.forms.User import UserCreationFormMail as Form
        r = HttpRequest()
        r.user = u = User.objects.get(id=1)
        self.assertEquals(userMethods.register(r),
            {'text': userMethods.ERROR_MESSAGES['register']['registred']})
        r.user = AnonymousUser()
        result = userMethods.register(r)
        result['form'] = FS(result['form'])
        self.assertEquals(result, {'form': FS(Form())})
        r.POST = {'register-email': 'a@aa.aa'}
        engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        r.session = engine.SessionStore("New")
        self.assertEquals(userMethods.register(r), {'text':
                            {'name': 'Anonymous'}, 'response': True})

    def test_load_settings(self):
        from anime.forms.User import UserEmailForm, UserNamesForm
        from anime.forms.Error import UploadMalListForm
        r = HttpRequest()
        r.user = u = User.objects.get(id=1)
        result = userMethods.load_settings(r)
        for name in result.keys():
            if name == 'mallist':
                continue
            result[name] = FS(result[name])
        self.assertEquals(result, {
                    'emailform': FS(UserEmailForm(instance=u)),
                    'usernames': FS(UserNamesForm(instance=u)),
                    'mallistform': FS(UploadMalListForm()),
                    'mallist': None})
        r.POST.update({'mallist': True, 'usernames': True, 'emailform': True})
        result = userMethods.load_settings(r)
        for name in ['emailform', 'usernames', 'mallistform']:
            result[name] = FS(result[name])
        self.assertEquals(result, {
            'emailform': FS(UserEmailForm(instance=u)),
            'usernames': FS(UserNamesForm(instance=u)),
            'mallistform': FS(UploadMalListForm(r.POST, r.FILES)),
            'mallist': None})

    def test_load_MalList(self):
        from os import stat, chmod
        from os.path import join as os_join
        from django.core.files.uploadedfile import SimpleUploadedFile
        from anime.forms.Error import UploadMalListForm
        r = HttpRequest()
        r.user = u = User.objects.get(id=1)
        filename = os_join(settings.MEDIA_ROOT, 'test', '1px.png')
        with open(filename, 'r') as fl:
            r.FILES={'file': SimpleUploadedFile(filename, fl.read())}
            cache.delete('MalList:1')
            r.POST.update({'mallist': True})
            res = userMethods.load_MalList(r)
            self.assertEquals(res, {
                'mallistform': res['mallistform'],
                'mallist': {'list': {'updated': True}}})
            res = userMethods.load_MalList(r)
            self.assertEquals(res['mallistform'].errors, {'__all__': [
                userMethods.ERROR_MESSAGES['mallist']['fast'].format(30)]
            })
            cache.delete('MalList:1')
            mode = (stat(settings.MEDIA_ROOT).st_mode & 0777)
            try:
                chmod(settings.MEDIA_ROOT, 444)
                fl.seek(0)
                res = userMethods.load_MalList(r)
                self.assertEquals(unicode(res['mallistform'].errors['__all__'][0]),
                    u"[Errno 13] Permission denied: '{0}'".format(
                        os_join(settings.MEDIA_ROOT, '1611px.png')))
            except:
                raise
            finally:
                chmod(settings.MEDIA_ROOT, mode)



class UserDBTest(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    def tearDown(self):
        cache.delete('Stat:1')
        cache.delete('userCss:1')
        super(TestCase, self).tearDown()

    def test_latest_status(self):
        from anime.models import UserStatusBundle
        from datetime import datetime
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        changed = UserStatusBundle.objects.filter(user=r.user).latest("changed").changed
        self.assertEquals(isinstance(changed, datetime), True)
        self.assertEquals(userMethods.latest_status(r), changed)
        self.assertEquals(userMethods.latest_status(r, 1), changed)
        self.assertEquals(userMethods.latest_status(r, user_id=2), None)

    def test_get_statistics(self):
        u = User.objects.get(id=1)
        cache.delete('Stat:1')
        self.assertEquals(userMethods.get_statistics(None), None)
        self.assertEquals(userMethods.get_statistics(u), [
            {'count': 1, 'anime__duration': 211, 'full': 24054, 'name': u'Want', 'anime__episodesCount': 114, 'custom': 211},
            {'count': 0, 'anime__duration': None, 'full': None, 'name': u'Now', 'anime__episodesCount': None, 'custom': None},
            {'count': 0, 'anime__duration': None, 'full': None, 'name': u'Done', 'anime__episodesCount': None, 'custom': None},
            {'count': 0, 'anime__duration': None, 'full': None, 'name': u'Dropped', 'anime__episodesCount': None, 'custom': None},
            {'count': 0, 'anime__duration': None, 'full': None, 'name': u'Partially watched', 'anime__episodesCount': None, 'custom': None},
            {'count': 1, 'full': 24054, 'name': 'Total', 'custom': 211}
        ])

    def test_get_styles(self):
        from anime.models import USER_STATUS
        u = User.objects.get(id=1)
        cache.delete('userCss:1')
        self.assertEquals(userMethods.get_styles(None), None)
        styles = [([''] if i != 1 else [u'1']) * 3 for i in range(0, len(USER_STATUS))]
        self.assertEquals(userMethods.get_styles(u), styles)


class UserRequestTest(TestCase):

    fixtures = ['requests.json']

    @create_user()
    def test_get_requests(self):
        u = User.objects.get(id=1)
        #FIXME: No actual result check
        self.assertNotEquals(userMethods.get_requests(u), {})
        self.assertEquals(userMethods.get_requests(u, 'new_field'), {})


class ExplorerTest(TestCase):

    fixtures = ['2trash.json']

    def test_FieldExplorer(self):
        ex = explorer.FieldExplorer(None)
        anime = AnimeItem.objects.get(id=1)
        self.assertEquals(ex.get_model(), None)
        self.assertEquals(ex.get_value(None, None), None)
        ex.set_field('set_field')
        self.assertRaisesMessage(explorer.GetError,
            ex.error_messages['error'].format(ex.error_messages['bad_field']),
            ex.get_value, anime, None)
        ex.set_field('_meta')
        self.assertRaisesMessage(explorer.GetError,
            ex.error_messages['error'].format(ex.error_messages['bad_field']),
            ex.get_value, anime, None)

    def test_FieldExplorer_fields(self):
        from anime.models import AnimeName
        fields = api.CatalogGetTypes()
        ex = explorer.FieldExplorer('anime')
        anime = AnimeItem.objects.get(id=1)
        self.assertEquals(ex.get_value(anime, None), None)
        for name in ['type', 'releaseType']:
            ex.set_field(name)
            self.assertEquals(ex.get_value(anime, None), anime.type)
        ex.set_field('releasedAt,endedAt')
        self.assertEquals(ex.get_value(anime, None), anime.release)
        ex.set_field('genre')
        self.assertEquals(len(ex.get_value(anime, None).split(', ')), anime.genre.count())
        for item in ['title', 'name', 'links', 'bundle']:
            ex.set_field(item)
            check_response(ex.get_value(anime, None), fields.funcs[item])
        anime.bundle = None
        self.assertEquals(ex.get_value(anime, None), None)

    @create_user()
    def test_FieldExplorer_state(self):
        from anime.models import UserStatusBundle, USER_STATUS
        ex = explorer.FieldExplorer('state')
        anime = AnimeItem.objects.get(id=1)
        r = HttpRequest()
        r.user = AnonymousUser()
        self.assertEquals(ex.get_value(anime, r),
                            ex.error_messages['bad_user'])
        r.user = User.objects.get(id=1)
        self.assertEquals(ex.get_value(anime, r),
                            {'state': 1, 'select': dict(USER_STATUS)})
        self.assertEquals(ex.get_value(AnimeItem.objects.get(id=2), r),
                            {'state': 0, 'select': dict(USER_STATUS)})
        sb = UserStatusBundle.objects.get(anime=anime, user=r.user)
        sb.state = 3
        sb.save()
        self.assertEquals(ex.get_value(anime, r), {'state': 3,
                            'select': dict(USER_STATUS), 'rating': 6})
        sb.state = 2
        sb.save()
        self.assertEquals(ex.get_value(anime, r), {'state': 2,
            'select': dict(USER_STATUS), 'completed': 1, 'all': 114})


class BaseTest(TestCase):

    fixtures = ['2trash.json']

    def test_get_data(self):
        from django.utils.datastructures import MultiValueDict
        r = HttpRequest()
        r.method = 'GET'
        self.assertEquals(coreMethods.get_data(r), {'text':
            coreMethods.ERROR_MESSAGES['get_data']['bad_request']})
        r.method = 'POST'
        self.assertEquals(coreMethods.get_data(r), {'text':
            coreMethods.ERROR_MESSAGES['get_data']['bad_id']})
        r.POST = {'id': 1}
        self.assertEquals(coreMethods.get_data(r), {'text':
            coreMethods.ERROR_MESSAGES['get_data']['bad_fields'].format(
                "'dict' object has no attribute 'getlist'")})
        r.POST = MultiValueDict({'id': '1'})
        self.assertEquals(coreMethods.get_data(r), {'text':
            coreMethods.ERROR_MESSAGES['get_data']['no_fields']})
        r.POST.setlist('field', ['title', 'None'])
        self.assertEquals(coreMethods.get_data(r), {'status': True,
            'response': 'get', 'id': 1, 'text':
                {'None': u'Error: Bad field', 'title': u'fe',
                'order': ['title', 'None']}
            })

    @create_user()
    def test_card(self):
        user = User.objects.get(id=1)
        anime = AnimeItem.objects.get(id=1)
        fields = api.CatalogGetTypes()
        cache.delete('card:1')
        self.assertRaises(AnimeItem.DoesNotExist, coreMethods.card, None, user)
        self.assertEquals(coreMethods.card('none', AnonymousUser()), {})
        result = coreMethods.card(1, user)
        for item in result.keys():
            if item == 'userstatus':
                f = {'count': 1, 'rating': 6, 'state': 1, 'statusName': u'Want'}
            elif item == 'anime':
                f = anime
            elif item == 'links':
                f = anime.links.order_by('linkType').all()
            elif item == 'bundle':
                f = fields.funcs[item].type['bundles']
            elif item == 'names':
                f = anime.animenames.values()
            else:
                f = fields.funcs[item]
            check_response(result[item], f)
        AnimeItem.objects.get(id=2).links.all().delete()
        cache.delete('card:2')
        result = coreMethods.card(2, user)
        self.assertEquals(list(result['links']), [])
        cache.delete('card:2')
        cache.delete('card:1')
