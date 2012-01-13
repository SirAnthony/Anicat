
from anime.models import USER_STATUS, LINKS_TYPES

class Noneable(type):
    pass

class CallableDict(dict):

    def __getitem__(self, item):
        item = dict.__getitem__(item)
        if not item:
            item = self.funcs.__getitem__(item)
        if callable(item):
            return item()
        else:
            return item

class FuzzyList(list):

    def set_count(self, count): #fuhack
        item = self.pop()
        self[:] = []
        self.extend([item] * count)

class NoneableDict(dict):
    pass

class Base(object):

    link_prefix = '/ajax/'
    link = ''
    params = {}
    returns = {}

    def __init__(self, prefix=''):
        if prefix:
            self.link_prefix = prefix

    def get_link(self):
        return self.link_prefix + self.link

class Register(Base):

    link = 'register/'

    params = {
        'register-username': unicode,
        'register-email': unicode,
        'register-password1': unicode,
        'register-password2': unicode
    }

    returns = {
        "status": True,
        "response": "login",
        "text": {"name": unicode}
    }

class Login(Base):

    link = 'login/'

    params = {
        'username': unicode,
        'password': unicode
    }

    returns = {
        "status": True,
        "response": "login",
        "text": {"name": unicode}
    }

class Add(Base):

    link = 'add/'

    params = {
        'title': unicode,
        'releaseType': int,
        'duration': int,
        'episodesCount': int,
        'releasedAt': unicode,
        'endedAt': unicode,
        'genre': tuple,
        'air': bool,
    }

    returns = {
        'response': 'add',
        'status': True,
        'id': int,
    }

class Get(Base):

    class Dict(CallableDict):

        def __init__(self):
            self.funcs = {
                'id': int,
                'title': unicode,
                'releaseType': unicode,
                'releasedAt': unicode,
                'releasedAt,endedAt': unicode,
                'release': unicode,
                'endedAt': unicode,
                'type': int,
                'releasedKnown': int,
                'endedKnown': int,
                'genre': unicode,
                'episodesCount': int,
                'air': bool,
                'name': FuzzyList([unicode,]),
                'bundle': FuzzyList([{"elemid": int, "name": unicode}]),
                'links': NoneableDict([(x[1], FuzzyList([unicode,])) for x in LINKS_TYPES[1:]]),
                'duration': int,
                'state': {"state": int, "select": dict(map(lambda x: (unicode(x[0]), x[1]), USER_STATUS))},
                'release': unicode,
                'order': tuple,
                'type': unicode,
            }

        def set_order(self, o):
            self.funcs['order'] = o
            self.clear()
            self['order'] = o
            for item in o:
                self[item] = self.funcs[item]

        def get_api(self):
            return self.funcs


    link = 'get/'

    params = {
        'field': tuple,
        'id': int
    }

    returns = {
        'response': 'get',
        'status': True,
        'id': int,
        'text': Dict()
    }
