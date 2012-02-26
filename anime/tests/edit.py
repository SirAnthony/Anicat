
import os
import datetime
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpRequest
from django.utils.unittest import skip
from django.test import TestCase

from anime import api
from anime.edit import ( edit, EditError, EditableDefault, Anime,
    State, Bundle, Name, Links, Request, Animerequest, Feedback, Image )
from anime.forms import json
from anime.models import AnimeItem
from anime.tests.functions import create_user, login, check_response, fill_params


class EditInitTest(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def test_editinit(self):
        a = api.Set()
        self.assertEquals(edit({}, modelname=None),
            {'text': u"'dict' object has no attribute 'user'"})
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        r.method = 'POST'
        e = a.get_returns('title')
        e.update({'status': False, 'response': 'form',
            'text': EditableDefault.error_messages['bad_model'],
            'id': 0, 'field': None, 'model': 'fvfv'})
        self.assertEquals(edit(r, modelname='fvfv'), e)
        e.update({'status': True,'text': [], 'model': 'bundle', 'response': 'edit'})
        self.assertEquals(edit(r, modelname='bundle'), e)


class EditDefaultTests(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    def test_EditableDefault_creation(self):
        r = HttpRequest()
        r.user = AnonymousUser()
        F = EditableDefault
        self.assertRaisesMessage(EditError,
            F.error_messages['not_loggined'], F, r)
        r.user = User.objects.get(id=1)
        r.user.date_joined = datetime.datetime.now()
        self.assertRaisesMessage(EditError,
            F.error_messages['wait'].format(settings.DAYS_BEFORE_EDIT),
            F, r)
        r.user.is_active = False
        self.assertRaisesMessage(EditError,
            F.error_messages['forbidden'], F, r)
        r.user = User.objects.get(id=1)
        self.assertRaisesMessage(EditError,
            F.error_messages['bad_id'], F, r, 'qwerty')
        self.assertRaisesMessage(EditError,
            F.error_messages['bad_model'], F, r, 1, 'qwerty')
        self.assertRaisesMessage(EditError,
            F.error_messages['bad_fields'], F, r, 1, 'anime', 'none')

    def test_EditableDefault_process(self):
        a = api.Forms()
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        f = EditableDefault(r, 0, 'bundle')
        self.assertRaisesMessage(EditError,
            f.error_messages['bad_request'], f.process, 'none')
        result = f.process('get')
        result['form'] = json.FormSerializer(result['form'])
        check_response(result, {'form': a.get_fields('bundle')})
        r.method = 'POST'
        result = f.process('get')
        result['form'] = json.FormSerializer(result['form'])
        check_response(result, {'form': a.get_fields('bundle')})
        result = f.process('form')
        result['form'] = json.FormSerializer(result['form'])
        check_response(result, {'form': a.get_fields('bundle'),
            'status': True, 'id': 0, 'text': api.Noneable(None)}) #lol
        #self.assertRaisesMessage(EditError,
        #    f.error_messages['bad_form'], f.process, 'get')
        f = EditableDefault(r, 1, 'anime', 'title')
        result = f.process('post')
        result['form'] = json.FormSerializer(result['form'])
        check_response(result, {'text': {'title': [u'This field is required.']},
            'id': 1, 'form': a.get_fields('anime', 'title')})
        #anime = AnimeItem.objects.get(id=1)
        #f = EditableDefault(r, 1, 'anime')
        #af = api.Add.params.copy()
        #for field in af.keys():
        #    if hasattr(anime, field):
        #        af[field] = getattr(anime, field)
        #af['genre'] = (1, 2)
        #f.request.POST.update(af)
        #def exception():
        #    raise Exception
        #f.last = exception
        #Test may break here
        #from django.db import connection, transaction
        #connection.cursor().execute('DROP TABLE anime_animeitem')
        #transaction.commit_unless_managed()
        #result = f.process('post')
        #result['form'] = json.FormSerializer(result['form'])
        #self.assertEquals(result, {'text': {'__all__':
        #    [f.error_messages['error'].format("no such table: anime_animeitem")]},
        #    'id': 1, 'form': result['form']})

    def test_EditableDefault_explore(self):
        from anime.core.explorer import FieldExplorer as FE
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        f = EditableDefault(r, 1, 'anime', 'title')
        self.assertEquals(f.explore_result(), {'text': 'fe'})
        f = EditableDefault(r, 1, 'bundle')
        f.field = 'get_field'
        self.assertEquals(f.explore_result(), {'status': False,
            'text': FE.error_messages['error'].format(
                FE.error_messages['bad_field'])})

    def test_EditError(self):
        self.assertEquals(unicode(EditError({'a': 'a'})), u"{'a': 'a'}")
        self.assertEquals(repr(EditError({'a': 'a'})), "EditError({'a': 'a'})")
        self.assertEquals(unicode(EditError(['a'])), u"[u'a']")
        self.assertEquals(repr(EditError(['a'])), u"EditError([u'a'])")


class EditSimpleTests(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    def test_Anime(self):
        a = api.Add()
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        f = Anime(r, 0, 'anime', 'title')
        r.method = 'POST'
        params = fill_params(a.get_params())
        f.request.POST.update(params)
        result = f.process('post')
        result['form'] = json.FormSerializer(result['form'])
        self.assertEquals(result, {'id': 0, 'form': result['form'], 'text': {'__all__': [
            f.error_messages['error'].format(Anime.error_messages['all_required'])]}})
        f = Anime(r, 0, 'anime')
        f.request.POST.update(params)
        self.assertEquals(f.process('post'), {'status': True,
            'text': None, 'response': 'edit', 'id': 3})
        #Test .last, no any checks, useless
        f = Anime(r, 1, 'anime', 'title')
        f.request.POST.update(params)
        result = f.process('post')

    def test_State(self):
        a = api.Add()
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        self.assertRaisesMessage(EditError,
                EditableDefault.error_messages['bad_id'], State, r, 0)
        params = fill_params(a.get_params())
        del params['genre']
        AnimeItem(**params).save()
        r.POST['state'] = -2
        f = State(r, 3, 'state')
        result = f.process('post')
        result['form'] = json.FormSerializer(result['form'])
        self.assertEquals(result, {'text': {
            'state': [u'Select a valid choice. -2 is not one of the available choices.']},
            'id': 3, 'form': result['form']})

    def test_Bundle(self):
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        r.POST['currentid'] = 0
        result = Bundle(r, 0, 'bundle').process('get')
        self.assertEqual(result, {'form': result['form']})
        f = Bundle(r, 0, 'bundle')
        self.assertEqual(f.explore_result(), {'text': []})
        f.request.POST['currentid'] = 1
        self.assertEqual(f.explore_result(), {'currentid': 1, 'text': {
            'bundles': [{'id': 2, 'title': u'dwkydani zjrq mj'},
            {'id': 1, 'title': u'fe'}], 'id': 1}})
        f = Bundle(r, 1, 'bundle')
        r.POST['currentid'] = 0
        self.assertEqual(f.explore_result(), {'currentid': 2, 'text': {
            'bundles': [{'id': 2, 'title': u'dwkydani zjrq mj'},
            {'id': 1, 'title': u'fe'}], 'id': 1}})
        f.last()


class EditRequestsTests(TestCase):

    fixtures = ['requests.json', '2trash.json']

    @create_user()
    def setUp(self):
        pass

    def test_Request(self):
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        f = Request(r, 0)
        self.assertEqual(f.explore_result(), {'form': f.form, 'text': None})
        f.last()

    def test_Image(self):
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        f = Image(r, 1, 'image')
        filename = os.path.join(settings.MEDIA_ROOT, 'test', '1px.png')
        resultname = os.path.join(settings.MEDIA_ROOT, '1619e0741c0526b10c74eda382595812bd6679adf84.png')
        if os.path.exists(resultname):
            os.unlink(resultname)
        with open(filename, 'r') as fl:
            f.request.FILES={'text': SimpleUploadedFile(filename, fl.read())}
            result = f.process('post')
            self.assertEquals(result, {'status': True, 'text': None,
                'response': 'edit', 'form': result['form'], 'id': 85})
        if os.path.exists(resultname):
            os.unlink(resultname)


class EditAnimebasedTests(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        pass

    def test_Name(self):
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        # Test EditableAnimeBased
        self.assertRaisesMessage(EditError,
                Name.error_messages['bad_id'], Name, r, 0)
        # Name test
        f = Name(r, 1, 'name')
        self.assertRaisesMessage(ValueError,
            f.error_messages['not_exists'].format('NoneType'), f.save, None, None)
        f.process('post') # Create f.form
        self.assertRaisesMessage(EditError, f.error_messages['no_names'],
            f.save, f.form, f.obj)
        f.request.POST = {'Name 0': 'new name'}
        self.assertEquals(f.process('post'), {'status': True, 'id': 1,
            'text': [u'new name'], 'response': 'edit'})
        f.request.POST = {'Name 0': 'New name 0', 'Name 1': 'New name 1'}
        self.assertEquals(f.process('post'), {'status': True, 'id': 1,
            'text': [u'New name 0', u'New name 1'], 'response': 'edit'})

    def test_Links(self):
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        f = Links(r, 1, 'links')
        self.assertRaisesMessage(ValueError,
            f.error_messages['not_exists'].format('NoneType'), f.save, None, None)
        f.request.POST = {'Link 0': u'example.com', 'Link type 0': 0,
            'Link 1': u'same.example.com', 'Link type 1': 0,
            'Link 2': u'same.example.com', 'Link type 2': 0,
            'Link 3': u'replaced.example.com', 'Link type 3': 0,}
        self.assertEquals(f.process('post'), {'status': True, 'text': {
            u'Other': [u'http://same.example.com/', u'http://example.com/',
            u'http://replaced.example.com/']}, 'response': 'edit', 'id': 1})
        f.request.POST = {'Link 0': u'example.com', 'Link type 0': 6, #changed
            'Link 1': u'replaced.example.com', 'Link type 1': 0}
        self.assertEquals(f.process('post'), {'status': True, 'text': {
            u'Other': [u'http://replaced.example.com/'],
            u'Official page': [u'http://example.com/']},
            'response': 'edit', 'id': 1})
        f.request.POST = {'Link 0': u'', 'Link type 0': 6,}
        self.assertEquals(f.process('post'), {'status': True,
                            'text': {}, 'response': 'edit', 'id': 1})
