import json
from django.test import TestCase
from anime import api
from anime.tests.functions import create_user, login, check_response, fill_params

class ErrorsTest(TestCase):

    def send_request(self, link, params, returns):
        response = self.client.post(link, params)
        ret = json.loads(response._container[0])
        try:
            check_response(ret, returns)
        except AssertionError, e:
            raise AssertionError('Error in response check. Data: %s, %s\nOriginal message: %s' % (
                    ret, returns, e.message))

    @create_user()
    def setUp(self):
        pass

    #def test_login(self):


    @login()
    def test_add(self):
        a = api.Add()
        link = a.get_link()
        self.send_request(link, {}, a.errors)
