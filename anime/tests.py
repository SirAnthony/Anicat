from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

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
        self.assert_(response["Location"].endswith('login/'))
        # login
        params['password'] = 'qwerty'
        response = self.client.post('/login/', params)
        self.assertEquals(response.status_code, 302)
        self.assert_(response["Location"].endswith('/'))
        # logout
        response = self.client.get('/logout/')
        self.assertEquals(response.status_code, 302)
        self.assert_(response["Location"].endswith('/'))

