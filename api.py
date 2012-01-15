
from anime.models import ANIME_TYPES, USER_STATUS, LINKS_TYPES


class Noneable(object):

    def __init__(self, t, d=None, *args, **kwargs):
        self.type = t
        self.default = d
        super(Noneable, self).__init__(*args, **kwargs)


class CallableDict(dict):

    def __getitem__(self, item):
        item = dict.__getitem__(self, item)
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


class TypedList(list):

    types = {}

    def __init__(self, types=None, *args, **kwargs):
        self._types = self.types = types
        super(TypedList, self).__init__(*args, **kwargs)

    def new_type(self, t):
        item = self.types[t]
        self[:] = []
        if isinstance(item, TypedList):
            self.types = item.types
            return
        if type(item) in (list, tuple):
            self.extend(item)
        else:
            self.append(item)

    def reset_types(self):
        self.types = self._types


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
                'endedAt': Noneable(unicode),
                'type': int,
                'releasedKnown': int,
                'endedKnown': int,
                'genre': unicode,
                'episodesCount': int,
                'air': bool,
                'name': FuzzyList([unicode,]),
                'bundle': {'id': int, 'bundles': FuzzyList([{"elemid": int, "name": unicode}])},
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

class Search(Base):

    link = 'search/'

    params = {
        'string': unicode,
        'field': Noneable(unicode, 'name'),
        'order': Noneable(unicode, 'title'),
        'page': Noneable(int, 0),
        'limit': Noneable(int, 30)
    }

    returns = {
        'response': 'search',
        'status': True,
        'text': {
            'count': int,
            'items': FuzzyList([{
                    'id': int,
                    'name': unicode,
                    'type': unicode,
                    'numberofep': int,
                    'release': unicode,
                    'air': bool
            },]),
            'page': int
        }
    }

def input_field(field, name=None):
    if not name:
        name = field
    return NoneableDict({"input": {"name": field, "value": Noneable(unicode), "label": Noneable(name[0].capitalize() + name[1:]), "type": unicode, "id": "id_%s" % field}})

def select_field(field, choices, name=None):
    if not name:
        name = field
    return NoneableDict({'select': {'choices': choices, 'required': True, 'id': u'id_%s' % field, 'name': field, 'label': Noneable(name[0].capitalize() + name[1:]), 'value': Noneable(int)}})

def textarea_field(field):
    return NoneableDict({u'textarea': {u'rows': Noneable(unicode), u'name': field, u'required': Noneable(True), u'cols': Noneable(unicode), u'label': Noneable(unicode), u'id': 'id_%s' % field}})

class Forms(Base):

    link = 'set/'

    params = {
        'id': int,
        'model': unicode,
        'field': Noneable(unicode)
    }

    returns = NoneableDict({
        'response': 'edit',
        'status': True,
        'id': int,
        'model': unicode,
        'field': Noneable(unicode),
        'form': TypedList({
            'state': select_field('state', USER_STATUS),
            'anime': TypedList({
                'title': input_field('title'),
                'releaseType': {"select": {"name": "releaseType", "required": True, "value": int, "label": "ReleaseType", "choices": ANIME_TYPES, "id": "id_releaseType"}},
                'episodesCount': input_field('episodesCount'),
                'duration': input_field('duration'),
                'releasedAt': input_field('releasedAt', 'released'),
                'endedAt': input_field('endedAt', 'Ended'),
                'air': input_field('air'),
            }),
            'links': [input_field('Link 0'), select_field('Link type 0', LINKS_TYPES)],
            'animerequest': textarea_field('text'),
            'image': input_field('text', 'File'),
            'request': textarea_field('text'),
            'feedback': textarea_field('text'),
            'bundle': [input_field('Bundle 0'), input_field('Bundle 1')],
            'name': [input_field('Name 0'), input_field('Name 1')],
        })
    })
