
import urllib

from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import BaseListView
from anime.utils import cache
from anime.utils.paginator import Paginator


class AnimeListView(TemplateResponseMixin, BaseListView):

    http_method_names = ['get']
    paginator_class = Paginator

    def get_context_data(self, **kwargs):
        self.filter()
        (link, cachestr) = self.get_link()
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

    def updated(self, cachestr):
        if not cache.key_valid(self.cache_name, cachestr):
            return True
        return not cache.latest(self.__class__.__name__, cachestr)

    def filter(self):
        pass
        #raise Exception(urllib.unquote(self.request.COOKIES['filter']))

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

    def updated(self, cachestr):
        if not self.ajax_call:
            if not cache.key_valid(self.cache_name, cachestr):
                return True
        self.data = data = cache.get('%s:%s' % (self.ajax_cache_name, cachestr))
        if not data or not 'list' in data:
            return True
        return not cache.latest(self.__class__.__name__, cachestr)

    def post(self, request, *args, **kwargs):
        if not self.ajax_call:
            return self.get(request, *args, **kwargs)
        else:
            return self.ajax(request, *args, **kwargs)

    def ajax(self, request, *args, **kwargs):
        "Implementation in subclasses"
        raise NotImplementedError

