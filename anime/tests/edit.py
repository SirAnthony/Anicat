
import datetime
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest
from django.test import TestCase

from anime import api
from anime.edit import ( edit, EditError, EditableDefault, Anime,
    State, Bundle, Name, Links, Request, Animerequest, Feedback, Image )
from anime.forms import json
from anime.tests.forms import FormsTest
from anime.tests.functions import create_user, login, check_response



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


class EditSimpleTests(FormsTest):

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

    def test_EditableDefault_explore(self):
        r = HttpRequest()
        r.user = User.objects.get(id=1)
        f = EditableDefault(r, 1, 'anime', 'title')
        self.assertEquals(f.explore_result(), {'text': 'fe'})
        #TODO: GetFieldError check

    def test_EditError(self):
        self.assertEquals(unicode(EditError({'a': 'a'})), u"{'a': 'a'}")
        self.assertEquals(repr(EditError({'a': 'a'})), "EditError({'a': 'a'})")
        self.assertEquals(unicode(EditError(['a'])), u"[u'a']")
        self.assertEquals(repr(EditError(['a'])), u"EditError([u'a'])")


