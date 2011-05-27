from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
import re

def getError(data):
    errors = {}
    mainerrors = re.findall(u'class="mainerror"[^>]*>([^>]*)<', data, re.M & re.U)
    if mainerrors:
        errors['__all__'] = mainerrors
    #Works wrong
    lists = re.findall(u'<div.*?name="(\w+)".*?class="errorlist".*?>(?=<li>(.*?)</li>)+<.*?</div>', data, re.M & re.U)
    errors.update(dict(lists))
    print errors
    return errors

class NormalTest(TestCase):

    def test_registration(self):
        params = {}
        register_link = '/register/'
        #First try bad attempts
        for param, value in (('register-username', 'nobody'), ('register-email', 'nobody@example.com'),
                             ('register-password1', 'qwerty')):
            params[param] = value
            response = self.client.post(register_link, params)
            self.assertEquals(response.status_code, 200)
        #Next try real register
        params["register-password2"] = "qwerty"
        response = self.client.post(register_link, params)
        self.assertEquals(response.status_code, 302)
        self.assert_(response["Location"].endswith('/'))

    def test_login_logout(self):
        User.objects.create_user('nobody2', 'nobody@example.com', 'qwerty')
        params = {'username': 'nobody2'}
        response = self.client.post('/login/', params)
        self.assertEquals(response.status_code, 200)
        # login
        params['password'] = 'qwerty'
        response = self.client.post('/login/', params)
        self.assertEquals(response.status_code, 302)
        self.assert_(response["Location"].endswith('/'))
        # logout
        response = self.client.get('/logout/')
        self.assertEquals(response.status_code, 302)
        self.assert_(response["Location"].endswith('/'))

    def test_add(self):
        #First login in
        User.objects.create_user('Editor', 'editor@example.com', 'qwerty')
        self.assertEquals(self.client.post('/login/', {'username': 'Editor', 'password': 'qwerty'}).status_code, 302)
        #Next - test
        add_link = '/add/'
        params = {'title': 12, 'releaseType': 6, 'episodesCount': 5, 'duration':  43,
                  'releasedAt': '2.4.1952', 'endedAt': '??.??.1952', 'air': True,
                  'genre': ('1','2'),
                  }
        #test blank input
        response = self.client.post(add_link, {})
        self.assertEquals(response.status_code, 200)
        print response.content
        #['close', 'context', 'cookies', 'csrf_processing_done', 'delete_cookie', 'flush', 'get', 'has_header', 'items', 'next', 'request', 'set_cookie', 'status_code', 'tell', 'template', 'templates', 'write']

        self.assertEquals(len(getError(response.content).keys()), len(params.keys()) - 1)
        #test addition
        response = self.client.post(add_link, params)
        print response.context['post']
        try:
            self.assertEquals(response.status_code, 302)
        except AssertionError:
            print getError(response.content)
            raise
        