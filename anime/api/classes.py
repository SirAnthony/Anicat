
import datetime
from anime.models import ANIME_TYPES, USER_STATUS, LINKS_TYPES
from anime.api.types import (data_to_string, Comment, Noneable,
            NoneableDict, CallableDict, FuzzyList, Field,
            CatalogGetTypes )
from anime.api.forms import from_form
from django.conf import settings

__all__ = ['Filter', 'Register', 'Login', 'Add', 'Get', 'Search',
           'Forms', 'Set', 'out', 'to_file']


class Base(object):

    link_prefix = '/ajax/'
    link = ''
    params = {}
    returns = {}
    returns_noarg = {}
    error = {}

    def __init__(self, prefix=''):
        if prefix:
            self.link_prefix = prefix
        for t, v in ((self.returns, True), (self.error, False)):
            if type(t) is dict:
                t.setdefault('status', v)

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
        noarg = ''
        if self.returns_noarg:
            noarg = """
    Response without arguments:
{0}""".format(data_to_string(self.returns_noarg, 2))
        return u"""{name}:
    {desc}
    Request target: {link}
    Request params:
{params}{noarg}
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

    def get_returns_noarg(self):
        return self.returns_noarg.copy()


class Filter(Base):
    """Apply filter to site output."""

    link = 'filter/'

    params = from_form('anime.forms.Error.FilterForm')

    returns = {
        'response': 'filter',
    }

    error = {
        'response': 'filter',
        'text': dict
    }


class Register(Base):
    """Register new account."""

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
    """Login to site."""

    link = 'login/'

    params = from_form('anime.forms.User.NotActiveAuthenticationForm')

    returns = {
        "response": "login",
        "text": {"name": unicode}
    }

    error = {
        'response': 'login',
        'text': dict,
    }


class Add(Base):
    """Add new record.
    This is a `form` field. It returns form if requested without parameters."""

    link = 'add/'

    params = from_form('anime.forms.ModelError.AnimeForm')

    returns = {
        'response': 'add',
        'id': int,
    }

    returns_noarg = {
        'title': Field('input', 'title'),
        'releaseType': Field('select', 'releaseType', choices=ANIME_TYPES),
        'duration': Field('input', 'duration', value=int),
        'episodesCount': Field('input', 'episodesCount', value=int),
        'releasedAt': Field('input', 'releasedAt', value=datetime.date),
        'endedAt': Field('input', 'endedAt', value=datetime.date),
        'genre': [Field('input', 'genre', value=int), Field('input', 'genre', value=int)],
        'air': Field('input', 'air', value=bool),
    }

    error = {
        'response': 'add',
        'text': dict,
    }


class Get(Base):
    """Get certain field for record."""

    link = 'get/'

    params = {
        'field': tuple,
        'id': int
    }

    returns = {
        'response': 'get',
        'id': int,
        'text': CatalogGetTypes()
    }

    error = Comment(u"""        No global errors for the get rerquest.
        All fields errors in response `text` parameter.""")


class Search(Base):
    """Search in database.
    Optional `fields` argument can be passed to retrive only certain fields in response."""

    link = 'search/'

    params = {
        'string': unicode,
        'order': Noneable(unicode, 'title'),
        'page': Noneable(int, 0),
        'limit': Noneable(int, settings.SEARCH_PAGE_LIMIT),
        'fields': Noneable(list, 'All item fields')
    }

    returns = {
        'response': 'search',
        'text': {
            'count': int,
            #FIXME: it different due to fields.
            'list': FuzzyList([
                Comment("The fields is differs depends on `fields` parameter. Default:"),
                {
                    'id': int,
                    'title': unicode,
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
        'text': list,
    }


class Forms(Base):
    """This API call returns JSON-serialized form for field."""

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
        'links': [Field('input', 'Link 0'), Field('select', 'Link type 0', choices=LINKS_TYPES)],
        'animerequest': Field('textarea', 'text', 'Request anime'),
        'image': Field('input', 'text', 'File'),
        'request': Field('textarea', 'text'),
        'feedback': Field('textarea', 'text', 'Please tell about your suffering'),
        'bundle': [Field('input', 'Bundle 0'), Field('input', 'Bundle 1')],
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
    """Change field."""

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


OUTPUT = [Search, Get, Filter, Login, Forms, Add, Set]

def out():
    for item in OUTPUT:
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
        for item in OUTPUT:
            fl.write(item.__str__())
            fl.write('\n')
