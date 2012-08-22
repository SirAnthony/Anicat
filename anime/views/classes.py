
import urllib
from hashlib import sha1
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import BaseListView
from anime.utils import cache
from anime.utils.paginator import Paginator



class AnimeListFilter(object):

    def __init__(self, data, user):
        self.user = user
        if type(data) == dict:
            self.data = data
        else:
            self.data = {}

    def get_cachename(self, cachestr):
        return sha1(cachestr + str(self.data)).hexdigest()

    def get_queryset(self, queryset):
        for key, value in self.data.items():
            field = getattr(self, key, None)
            if callable(field):
                queryset = field(queryset, value)
            else:
                filtercase = key + self.get_relation(*value[1:])
                queryset = queryset.filter(**{filtercase: value[0]})
        return queryset

    def get_relation(self, relation, equal):
        if relation in ['__lt', '__gt']:
            return relation + 'e' * bool(equal)
        elif equal:
            return '__exact'
        return ''

    def releaseType(self, queryset, value):
        return queryset.filter(releaseType__in=value)

    def genre(self, queryset, value):
        return queryset.filter(genre__in=value)

    def state(self, queryset, value):
        return queryset.filter(statusbundles__user=self.user,
                               statusbundles__state__in=value)


class AnimeListView(TemplateResponseMixin, BaseListView):

    http_method_names = ['get']
    paginator_class = Paginator
    listfilter = None

    def get_queryset(self):
        queryset = super(AnimeListView, self).get_queryset()
        return self.get_filter().get_queryset(queryset)

    def get_context_data(self, **kwargs):
        (link, cachestr) = self.get_link()
        cachestr = self.get_filter().get_cachename(cachestr)
        context = {'cachestr': cachestr, 'link': link}
        if self.updated(cachestr):
            context.update(self.create_context_data(cachestr, link, **kwargs))
            cache.update_named_cache(cachestr)
            cache.clean_cache(self.cache_name, cachestr)
        return context

    def create_context_data(self, cachestr, link, **kwargs):
        queryset = kwargs.pop('object_list')
        page_size = self.get_paginate_by(queryset)
        paginator = None
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            paginator.set_order(self.order)
            paginator.set_cachekey(link['link'])
            context = {
                'pages': {'current': page.number,
                    'start': page.start_index(),
                    'items': paginator,
                },
                'list': queryset,
            }
        else:
            context = {'pages': {}, 'list': queryset}
        context.update(kwargs)
        return context

    def updated(self, cachestr, keys={}):
        if not cache.key_valid(self.cache_name, cachestr):
            return True
        return not cache.latest(self.__class__.__name__, cachestr, keys)

    def get_filter(self):
        if not self.listfilter:
            self.listfilter = AnimeListFilter(
                self.request.session.get('filter', None), self.request.user)
        return self.listfilter

    def get_link(self):
        "Implementation in subclasses"
        raise NotImplementedError

    def check_parameters(self, request, *args, **kwargs):
        "Implementation in subclasses"
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        self.check_parameters(request, *args, **kwargs)
        return super(AnimeListView, self).get(request, *args, **kwargs)


class AnimeAjaxListView(AnimeListView):

    http_method_names = ['get', 'post']
    ajax_call = False

    def get_context_data(self, **kwargs):
        (link, cachestr) = self.get_link()
        cachestr = self.get_filter().get_cachename(cachestr)
        context = {}
        if not self.ajax_call:
            context.update({'cachestr': cachestr, 'link': link})
        if self.updated(cachestr):
            context.update(self.create_context_data(cachestr, link, **kwargs))
            cache.clean_cache(self.cache_name, cachestr)
            if not self.ajax_call:
                cache.update_named_cache(cachestr)
            self.data = context
            #FIXME: One useless query for caching paginator
            cache.cset('%s:%s' % (self.ajax_cache_name, cachestr), context, 0)
        elif self.data:
            context = self.data
        return context

    def updated(self, cachestr, keys={}):
        if not self.ajax_call:
            if not cache.key_valid(self.cache_name, cachestr):
                return True
        self.data = data = cache.get('%s:%s' % (self.ajax_cache_name, cachestr))
        if not data or not 'list' in data:
            return True
        return not cache.latest(self.__class__.__name__, cachestr, keys={})

    def post(self, request, *args, **kwargs):
        if not self.ajax_call:
            return self.get(request, *args, **kwargs)
        else:
            return self.ajax(request, *args, **kwargs)

    def ajax(self, request, *args, **kwargs):
        "Implementation in subclasses"
        raise NotImplementedError

