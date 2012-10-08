import datetime

from django.contrib.auth.models import User, AnonymousUser
from django.test.client import RequestFactory

from anime.utils.misc import is_iterator
from anime.api import types as apiTypes
from anime.api import classes as apiClasses

request_factory = RequestFactory()

user = 'nobody'
email = 'nobody@example.com'
passwd = 'qwerty'


def login(u=None, pwd=None):
    def wrap(f):
        def d_login(self, *args, **kwargs):
            params = {'username': u or user, 'password': pwd or passwd}
            self.assertEquals(self.client.post('/login/', params).status_code, 302)
            f(self, *args, **kwargs)
        return d_login
    return wrap


def create_user(u=None, e=None, p=None, lng=False):
    def wrap(f):
        def d_create(self, *args, **kwargs):
            us = User.objects.create_user(u or user, e or email, p or passwd)
            us.date_joined = datetime.date.today() - datetime.timedelta(20)
            us.save()
            f(self, *args, **kwargs)
        return d_create
    return wrap


def fake_request(*args, **kwargs):
    user = kwargs.pop('_user', AnonymousUser())
    request = request_factory.post(*args, **kwargs)
    request.user = user
    request.session = {}
    return request


def check_response(response, origin, *args, **kwargs):

    if origin is None:
        raise AssertionError('Original is None: %s' % origin)

    if isinstance(origin, dict):
        if not isinstance(response, dict):
            raise AssertionError('%s not match original type: %s' % (response, origin))
        #elif not isinstance(origin, apiTypes.NoneableDict) and \
        #        len(origin.keys()) != len(response.keys()):
        #    raise AssertionError('%s fields count differs from %s' % (response, origin))
        else:
            for key, item in origin.items():
                try:
                    check_response(response[key], item, *args, **kwargs)
                except KeyError:
                    # Field may be absent if value is None
                    if item is not None and not isinstance(origin, apiTypes.NoneableDict) and \
                       not isinstance(item, apiTypes.Noneable):
                        raise AssertionError('%s not match original: %s;\nKey: %s, item: %s' % (response, origin, key, item))
            return

    if isinstance(origin, basestring):
        if not isinstance(response, basestring):
            raise AssertionError('%s is not string. Type does not match: %s' % (response, origin))
        elif not origin == response:
            raise AssertionError('%s not match original: %s' % (response, origin))
        return

    if is_iterator(origin):
        if not is_iterator(response):
            raise AssertionError('%s not match original type: %s' % (response, origin))
        if isinstance(origin, apiTypes.FuzzyList):
            origin.set_count(len(response))
        for i in range(0, len(origin)):
            try:
                check_response(response[i], origin[i], *args, **kwargs)
            except IndexError:
                raise AssertionError('%s not match original: %s. Item %s not found' % (response, origin, origin[i]))
            except Exception, e:
                raise e
        return

    if isinstance(origin, bool):
        if not isinstance(response, bool):
            raise AssertionError('%s not match original type: %s' % (response, origin))
        else:
            if not response == origin:
                raise AssertionError('%s not match original: %s' % (response, origin))
        return

    if isinstance(origin, apiTypes.Noneable):
        if response is not None:
           check_response(response, origin.type)
        return

    if isinstance(origin, type):
        if not type(response) == origin:
            if origin is datetime.date and type(response) is unicode: #rewrite
                return
            if origin != unicode or type(response) not in (str, bool, int, float, long, complex):
                raise AssertionError('%s type (%s) not match original type: %s' % (response, type(response), origin))
        return

    if callable(origin):
        check_response(response, origin(*args, **kwargs), *args, **kwargs) #le fu


def fill_params(sample, data={}):

    if isinstance(sample, apiClasses.Base):
        return fill_params(sample.get_params(), data)

    if isinstance(sample, apiTypes.Field):
        return fill_params(sample.value())

    if isinstance(sample, apiTypes.MultiType):
        return fill_params(sample.types[0], data)

    for t in (basestring, str, bool, int, float, long, complex, type(None)):
        if isinstance(sample, t):
            return sample

    if isinstance(sample, apiTypes.Noneable):
        t = sample.default if sample.default is not None else sample.type
        return fill_params(t)

    if isinstance(sample, dict):
        params = {}
        for key, value in sample.copy().items():
            param = fill_params(data[key] if key in data else value)
            if param is not None:
                params[key] = param
        return params

    #~ if isinstance(sample, list):
        #~ params = []
        #~ for value in sample[:]:
            #~ try:
                #~ default = data.pop()
            #~ except IndexError:
                #~ default = None
            #~ param = fill_params(default if default else value)
            #~ if param is not None:
                #~ params.append(param)
        #~ return params

    if is_iterator(sample):
        return [fill_params(s) for s in sample]

    if isinstance(sample, type):
        if sample in (unicode, str):
            return u'a'
        elif sample is int:
            return 1
        elif sample is bool:
            return False
        elif sample is list:
            return [1,2]
        elif sample in (datetime.date, datetime.datetime):
            return datetime.date.today()
        else:
            raise TypeError('Not supported type: {0}'.format(sample))

