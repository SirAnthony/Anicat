# -*- coding: utf-8 -*-
import datetime
from anime.models import USER_STATUS, LINKS_TYPES
from anime.utils.misc import is_iterator
from django.utils.encoding import smart_unicode

DEPTH_FORMATER = ' '

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
    t = DEPTH_FORMATER * depth * 4
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


class Comment(unicode):
    pass


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
            default = ". Default: {0}".format(self.default) if self.default else ''
            name = self.type.__name__
            t = DEPTH_FORMATER * depth * 4
            #FIXME: depth passed from parent and not 0
            return Comment(u"{name} or nothing{default}".format(**locals()))
        else:
            return self.type


class NoneableDict(dict):
    pass


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


class MultiType(object):
    def __init__(self, *args):
        self.types = args

    def __unicode__(self):
        return u' or '.join([arg.__name__ for arg in self.types])
    __name__ = property(__unicode__)


class FileType(object):

    def __unicode__(self):
        return u'file'
    __name__ = property(__unicode__)


class WidgetFieldType(type):
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
        self.default_obj = kwargs.pop('default_obj', None)
        self.attrs = kwargs

    def __unicode__(self):
        return smart_unicode(self.field())

    #TODO: make something with name
    def props(self, text=True):
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
        if self.default_obj is not None and not text:
            attr['value'] = self.default_obj
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
