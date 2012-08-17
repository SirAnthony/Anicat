
import datetime
from django.utils.encoding import smart_unicode
from anime.models import ANIME_TYPES, USER_STATUS, LINKS_TYPES, DATE_FORMATS
from anime.utils.misc import is_iterator

# string.format is useless shit
def data_to_string(data, depth=0):
    if isinstance(data, Comment):
        return smart_unicode(data)
    elif isinstance(data, basestring):
        return u'"%s"' % smart_unicode(data)
    elif type(data) is type:
        return unicode(data.__name__)
    elif data is None:
        return u'nothing'
    elif isinstance(data, datetime.datetime) or \
         isinstance(data, datetime.date):
        return unicode(data.strftime(DATE_FORMATS[0]))
    elif isinstance(data, Noneable):
        s = '\n%s' if isinstance(data.type, dict) else '%s'
        return s % data_to_string(data.to_string(depth), depth)
    elif isinstance(data, (FuzzyList, CatalogGetTypes)):
        return data_to_string(data.to_string(depth), depth)
    t = ' ' * depth * 4
    if isinstance(data, dict):
        return u',\n'.join(
            [u'{t}{0}: {n}{1}'.format(k, data_to_string(v, depth + 1),
                t=t, n='\n' if isinstance(v, dict) else '')
                for k, v in data.items()])
    elif is_iterator(data):
        return u"""[
{0}
{t}]""".format('\n'.join(
        ['{t}{0}'.format(data_to_string(value, depth + 1),
            t=t if not isinstance(value, dict) else '')
                for value in data]), t=t)
    return smart_unicode(data)


class Noneable(object):

    def __init__(self, t, d=None, *args, **kwargs):
        self.type = t
        self.default = d
        super(Noneable, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return unicode(self.to_string())

    def to_string(self, depth=0):
        if isinstance(self.type, type):
            return Comment(u"{0} or nothing".format(self.type.__name__))
        else:
            return self.type


class CallableDict(dict):

    def __getitem__(self, item):
        try:
            item = dict.__getitem__(self, item)
        except:
            item = self.funcs.__getitem__(item)
        if callable(item) and not isinstance(item, type):
            return item()
        else:
            return item

class FuzzyList(list):
    """This list may have variable items count. All items have the same structure"""

    def set_count(self, count): #fuhack
        item = self.pop()
        self[:] = []
        self.extend([item] * count)

    def to_string(self, depth):
        s = [Comment(self.__doc__)]
        s.extend(self)
        return s


class NoneableDict(dict):
    pass


class Comment(unicode):
    pass

class Field(object):

    def __init__(self, t, name, label=None, fid=None, **kwargs):
        if t not in ['input', 'select', 'textarea']:
            raise ValueError('Field type not supported')
        self.type = t
        self.name = name
        self.label = label if label else name[0].capitalize() + name[1:]
        self.id = fid if fid else 'id_{0}'.format(name)
        self.default = kwargs.pop('default', None)
        self.attrs = kwargs

    def __unicode__(self):
        return smart_unicode(self.field())

    #TODO: make something with name
    def props(self):
        func = getattr(self, self.type, None)
        attr = {
            "name": self.name,
            "value": Noneable(
                self.attrs['value'] if 'value' in self.attrs else unicode,
                self.default
            ),
            "label": Noneable(self.label),
            "id": self.id
        }
        if callable(func):
            attr.update(func())
        return attr

    def value(self):
        return self.props()['value']

    def field(self):
        return NoneableDict({self.type: self.props()})

    def select(self):
        if 'choices' not in self.attrs:
            raise AttributeError('Choices not passed.')
        return {'choices': self.attrs['choices'],
                'value': Noneable(int, self.default)}

    def textarea(self):
        return {
            'rows': Noneable(unicode),
            'cols': Noneable(unicode),
        }


class CatalogGetTypes(CallableDict):
    """This dictionary may have one or many keys/values from bellow. Order of fields in "order" named list"""
    api_keys = ['id', 'title', 'type', 'release', 'genre', 'duration',
                'episodesCount', 'air', 'name', 'bundle', 'links',
                'state', 'order']

    def __init__(self):
        self.funcs = {
            'id': int,
            'title': unicode,
            'releaseType': unicode,
            'releasedAt': unicode,
            'releasedAt,endedAt': unicode,
            'release': unicode,
            'endedAt': Noneable(unicode),
            'releasedKnown': int,
            'endedKnown': int,
            'genre': unicode,
            'episodesCount': int,
            'air': bool,
            #TODO: It must be 'names'
            'name': FuzzyList([unicode,]),
            'bundle': Noneable({'id': int, 'bundles': FuzzyList([{"id": int, "title": unicode}])}),
            'links': NoneableDict([(x[1], FuzzyList([unicode,])) for x in LINKS_TYPES[1:]]),
            'duration': int,
            'state': {"state": int, "select": dict(map(lambda x: (unicode(x[0]), x[1]), USER_STATUS))},
            'order': tuple,
            'type': unicode,
        }

    def to_string(self, depth):
        s = {}
        for i in self.api_keys:
            s[i] = self.funcs[i]
        return {Comment(self.__doc__): s}

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
    error = {}

    def __init__(self, prefix=''):
        if prefix:
            self.link_prefix = prefix

    @classmethod
    def __str__(cls):
        c = cls()
        return str(c.__unicode__())

    def __unicode__(self):
        name = self.__class__.__name__
        desc = getattr(self, '__doc__', None) or 'No description.'
        link = self.get_link()
        params = data_to_string(self.string_params(), 2)
        response = data_to_string(self.string_returns(), 2)
        error = data_to_string(self.error, 2)
        return u"""{name}:
    {desc}
    Request target: {link}
    Request params:
{params}
    Response object:
{response}
    Error object:
{error}
""".format(**locals())

    def get_link(self):
        return self.link_prefix + self.link

    def string_params(self):
        return self.get_params()

    def get_params(self):
        return self.params.copy()

    def string_returns(self):
        return self.get_returns()

    def get_returns(self):
        return self.returns.copy()


class Register(Base):

    link = 'register/'

    params = {
        'register-email': unicode,
    }

    returns = {
        "status": True,
        "response": "login",
        "text": {"name": unicode}
    }

    error = {
        'response': 'register',
        'status': False,
        'text': dict,
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

    error = {
        'response': 'login',
        'status': False,
        'text': dict,
    }


class Add(Base):

    link = 'add/'

    params = {
        'title': Field('input', 'title'),
        'releaseType': Field('select', 'releaseType', choices=ANIME_TYPES),
        'duration': Field('input', 'duration', value=int),
        'episodesCount': Field('input', 'episodesCount', value=int),
        'releasedAt': Field('input', 'releasedAt', value=datetime.date),
        'endedAt': Field('input', 'endedAt', value=datetime.date),
        'genre': [Field('input', 'genre', value=1), Field('input', 'genre', value=2)],
        'air': Field('input', 'air', value=bool),
    }

    returns = {
        'response': 'add',
        'status': True,
        'id': int,
    }

    error = {
        'response': 'add',
        'status': False,
        'text': dict,
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

    error = Comment(u"""        No global errors for the get rerquest.
        All fields errors in response text""")


class Search(Base):

    link = 'search/'

    params = {
        'string': unicode,
        'order': Noneable(unicode, 'title'),
        'page': Noneable(int, 0),
        'limit': Noneable(int, 30)
    }

    returns = {
        'response': 'search',
        'status': True,
        'text': {
            'count': int,
            'list': FuzzyList([{
                    'id': int,
                    'name': unicode,
                    'type': unicode,
                    'episodes': int,
                    'release': unicode,
                    'air': bool,
            },]),
            'pages': {
                'current': int,
                'start': int,
                'items': list,
            }
        }
    }

    error = {
        'response': 'search',
        'status': False,
        'text': list,
    }


class Forms(Base):

    api_keys = ['state', 'anime', 'links', 'bundle', 'name']

    link = 'form/'

    params = {
        'id': int,
        'model': unicode,
        'field': Noneable(unicode)
    }

    returns = NoneableDict({
        'response': 'form',
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
            'episodesCount': Field('input', 'episodesCount', value=int),
            'duration': Field('input', 'duration', value=int),
            'releasedAt': Field('input', 'releasedAt', 'Released', value=datetime.date),
            'endedAt': Field('input', 'endedAt', 'Ended', value=datetime.date),
            'air': Field('input', 'air'),
        },
        'links': [Field('input', 'Link 0', default='http://example.com'), Field('select', 'Link type 0', default=0, choices=LINKS_TYPES)],
        'animerequest': Field('textarea', 'text', 'Request anime'),
        'image': Field('input', 'text', 'File'),
        'request': Field('textarea', 'text'),
        'feedback': Field('textarea', 'text', 'Please tell about your suffering'),
        'bundle': [Field('input', 'Bundle 0', default=1), Field('input', 'Bundle 1', default=2)],
        'name': [Field('input', 'Name 0'), Field('input', 'Name 1')],
    }

    error = {
        'response': 'form',
        'status': False,
        'model': unicode,
        'field': Noneable(unicode),
        'id': unicode,
        'text': unicode,
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
            if type(item) is dict:
                for key, value in item.items():
                    r['form'].append(value.field())
            else:
                r['form'].append(item.field())
        return r

    def string_returns(self):
        r = self.returns
        f = {}
        for i in self.api_keys:
            f[i] = self.forms[i]
        r['form'] = [Comment("This data is serialised form fields list. Field types:"), f]
        return r


class Set(Get):

    link = 'set/'

    params = {
        'id': int,
        'model': unicode,
        'field': Noneable(unicode),
    }

    returns = {
        'response': 'edit',
        'status': True,
        'id': int,
        'field': Noneable(unicode),
        'model': unicode,
        'text': dict,
    }

    error = {
        'response': 'form',
        'status': False,
        'model': unicode,
        'field': Noneable(unicode),
        'id': int,
        'text': dict,
    }

    types = CatalogGetTypes()
    forms = Forms()

    def get_returns(self, t):
        r = self.returns.copy()
        r['text'] = self.types[t]
        return r

    def string_returns(self):
        return self.returns.copy()

    def get_params(self, t, f=None):
        form = self.forms.get_fields(t, f)
        ret = self.params.copy()
        for item in form:
            attr = item.props()
            ret[attr['name']] = attr['value']
        return ret

    def string_params(self):
        return self.params.copy()


def out():
    for item in [Search, Get, Login, Forms, Add, Set]:
        print item.__str__()


def to_file(filename):
    with open(filename, 'w') as fl:
        fl.write(u"""API reference.
Notes:
    Ajax requests must be sent to /ajax/$target.
    Response is a json structure with 3 mandatory fields:
        response - string, type of response,
        status - bool, result of request process,
        text - different, body of response.

""")
        for item in [Search, Get, Login, Forms, Add, Set]:
            fl.write(item.__str__())
            fl.write('\n')
