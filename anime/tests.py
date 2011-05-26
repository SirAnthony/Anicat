from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
import re

def getError(data):
    #print data
    mainerrors = re.findall(u'class="mainerror"[^>]*>([^>]*)<', data, re.M & re.U)
    lists = re.findall(u'class="errorlist"[^>]*>(?=<li>([^>]*)</li>)+<', data, re.M & re.U)
    print lists

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
        params = {#'title': 12, 'releaseType': 6, 'episodesCount': 5, 'duration':  43,
                  #'releasedAt': '2.4.1952', 'endedAt': '??.??.1952', 'air': True,
                  #'genre': (1,2,3)
                  }
        response = self.client.post(add_link, params)
        getError(response.content)
        