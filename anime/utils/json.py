
import datetime
import simplejson
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.functional import Promise
from anime.models import DATE_FORMATS
from anime.utils.misc import is_iterator


def prepare_data(data, depth=None):

    #Not works with 0
    depth = depth or 7

    if depth <= 0:
        return smart_unicode(data)

    if isinstance(data, basestring):
        return smart_unicode(data)

    elif isinstance(data, (bool, int, long, float, complex, JSONFunction)):
        return data

    elif data is None:
        return data

    elif isinstance(data, datetime.datetime) or \
         isinstance(data, datetime.date):
        return data.strftime(DATE_FORMATS[0])

    elif isinstance(data, Promise):
        return force_unicode(data)

    elif isinstance(data, dict):
        return dict((key, prepare_data(value, depth - 1))
                            for key, value in data.iteritems())

    elif is_iterator(data):
        return [prepare_data(value, depth - 1) for value in data]

    return smart_unicode(data)


class JSONFunction(object):
    def __init__(self, name, *argv):
        self.name = name
        self.args = [prepare_data(arg, -1) for arg in argv]

    def __unicode__(self):
        return u'{0}({1})'.format(self.name, ','.join(self.args))

    def toJSON(self):
        return u'${0}$'.format(unicode(self))


class JSONFunctionCaller(JSONFunction):
    def toJSON(self):
        return u'$function(){{return {0};}}$'.format(unicode(self))


class JSONFunctionEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if isinstance(o, JSONFunction):
            return o.toJSON()
        return simplejson.JSONEncoder.default(self, o)

