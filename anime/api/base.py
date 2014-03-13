
from anime.api.types import data_to_string
from anime.api.forms import params_from_view, returns_from_view

class ApiBase(object):

    link_prefix = '/ajax/'
    link = ''
    response = 'error'

    def __init__(self, prefix=''):
        for attr in ['params', 'returns', 'returns_noarg', 'error']:
            if not getattr(self, attr, None):
                setattr(self, attr, {})

        if prefix:
            self.link_prefix = prefix
        view = getattr(self, 'view', None)
        if isinstance(view, basestring):
            (view_path, view_name) = view.rsplit('.', 1)
            self.view = view = getattr(
                __import__(view_path, globals(), {}, [view_name]), view_name)
        if view:
            self.params['text'] = params_from_view(view)
            self.returns['text'] = returns_from_view(view)
        for t, v in ((self.returns, True), (self.error, False)):
            if type(t) is dict:
                t.setdefault('status', v)
                t.setdefault('response', self.response)

    def get_cachestr(self, request, args):
        if not hasattr(self, 'view') or not isinstance(args, dict):
            return ''
        instance = self.view()
        setattr(instance, 'kwargs', {})
        setattr(instance, 'request', request)
        instance.check_parameters(instance.request, **args)
        link = instance.get_link()
        return instance.get_cachestr(link)

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

