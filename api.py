
from anime.models import ANIME_TYPES, USER_STATUS, LINKS_TYPES


class Noneable(object):

    def __init__(self, t, d=None, *args, **kwargs):
        self.type = t
        self.default = d
        super(Noneable, self).__init__(*args, **kwargs)


class CallableDict(dict):

    def __getitem__(self, item):
        try:
            item = dict.__getitem__(self, item)
        except:
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


class CatalogGetTypes(CallableDict):

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
            self['order'] = o
            self.set_type(o)

        def set_type(self, t):
            self.clear()
            if type(t) in (list, tuple):
                for item in t:
                    self[item] = self.funcs[item]
            elif isinstance(t, basestring):
                self[t] = self.funcs[t]

        def get_api(self):
            return self.funcs


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

    link = 'get/'

    params = {
        'field': tuple,
        'id': int
    }

    returns = {
        'response': 'get',
        'status': True,
        'id': int,
        'text': CatalogGetTypes()
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



class Field(object):

    def __init__(self, t, name, label=None, fid=None, **kwargs):
        if t not in ['input', 'select', 'textarea']:
            raise ValueError('Field type not supported')
        self.type = t
        self.name = name
        self.label = label if label else name[0].capitalize() + name[1:]
        self.id = fid if fid else 'id_{0}'.format(name)
        self.attrs = kwargs
        self.attr = self.props()
        self.field = self._field()

    #TODO: make something with name
    def props(self):
        func = getattr(self, self.type, None)
        attr = {
            "name": self.name,
            "value": Noneable(unicode),
            "label": Noneable(self.label),
            "id": self.id
        }
        if callable(func):
            attr.update(func())
        return attr

    def _field(self):
        return NoneableDict({self.type: self.attr})

    def select(self):
        if 'choices' not in self.attrs:
            raise AttributeError('Choices not passed.')
        return {'choices': self.attrs['choices'],
                'value': Noneable(int)}

    def textarea(self):
        return {
            'rows': Noneable(unicode),
            'cols': Noneable(unicode),
        }


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
        'form': list
    })

    forms = {
        'state': Field('select','state', choices=USER_STATUS),
        'anime': {
            'title': Field('input', 'title'),
            'releaseType': Field('select', 'releaseType', choices=ANIME_TYPES),
            'episodesCount': Field('input', 'episodesCount'),
            'duration': Field('input', 'duration'),
            'releasedAt': Field('input', 'releasedAt', 'Released'),
            'endedAt': Field('input', 'endedAt', 'Ended'),
            'air': Field('input', 'air'),
        },
        'links': [Field('input', 'Link 0'), Field('select', 'Link type 0', choices=LINKS_TYPES)],
        'animerequest': Field('textarea', 'text', 'Request anime'),
        'image': Field('input', 'text', 'File'),
        'request': Field('textarea', 'text'),
        'feedback': Field('textarea', 'text', 'Please tell about your suffering'),
        'bundle': [Field('input', 'Bundle 0'), Field('input', 'Bundle 1')],
        'name': [Field('input', 'Name 0'), Field('input', 'Name 1')],
    }

    def get_fields(self, t, f=None):
        ret = []
        if not isinstance(self.forms[t], Field) and f is not None:
            form = self.forms[t][f]
        else:
            form = self.forms[t]
        if type(form) in (tuple, list):
            ret.extend(form)
        else:
            ret.append(form)
        return ret

    def get_returns(self, t, f=None):
        r = self.returns
        r['form'] = []
        for item in self.get_fields(t, f):
            r['form'].append(item.field)
        return r


class Set(Get):

    link = 'set/'

    params = {
        'id': int,
        'model': unicode,
        'field': Noneable(unicode),
        'set': True
    }

    returns = {
        'response': 'edit',
        'status': True,
        'id': int,
        'field': Noneable(unicode),
        'model': unicode,
        'text': dict,
    }

    types = CatalogGetTypes()
    forms = Forms()

    def get_returns(self, t):
        r = self.returns
        r['text'] = self.types[t]
        return r

    def get_params(self, t, f=None):
        form = self.forms.get_fields(t, f)
        ret = self.params
        for item in form:
            ret[item.attr['name']] = item.attr['value']
        return ret

