
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase

from anime import api
from anime.edit import edit
from anime.tests.functions import create_user, login, last_record

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
        e.update({'status': False, 'text': u'Bad model name passed.',
                  'id': 0, 'field': None, 'model': 'fvfv'})
        self.assertEquals(edit(r, modelname='fvfv'), e)
        e.update({'status': True,'text': [], 'model': 'bundle'})
        self.assertEquals(edit(r, modelname='bundle'), e)
