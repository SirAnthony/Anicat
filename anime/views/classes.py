
import urllib
from django.db.models.fields import FieldDoesNotExist
from django.http import Http404
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import BaseListView
from django.utils.translation import ugettext_lazy as _
from anime.utils import cache
from anime.utils.paginator import Paginator
from anime.views.ajax import ajaxResponse
from anime.views.filter import AnimeListFilter


class AnimeListView(TemplateResponseMixin, BaseListView):

    http_method_names = ['get']
    paginator_class = Paginator
    filter_class = AnimeListFilter

    def get_queryset(self):
        queryset = super(AnimeListView, self).get_queryset()
        return self._filter.get_queryset(queryset)

    def get_context_data(self, **kwargs):
        (link, cachestr) = self.get_link()
        cachestr = self._filter.get_cachestring(cachestr)
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
            paginator.set_cachekey(self._filter.get_cachestring(link['link']))
            pages = range(1, paginator.num_pages + 1)
            if not getattr(self, 'pages_numeric', False):
                pages = paginator.get_names()
            context = {
                'pages': {'current': page.number,
                    'start': page.start_index(),
                    'count': paginator.num_pages,
                    'items': pages,
                },
                'head': getattr(self, 'fields', None),
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
        if not hasattr(self, '_listfilter'):
            self._listfilter = self.filter_class(
                self.request.session.get('filter', None), self.request.user.id)
        return self._listfilter
    _filter = property(get_filter)

    def get_link(self):
        "Implementation in subclasses"
        raise NotImplementedError

    def check_parameters(self, request, *args, **kwargs):
        "Implementation in subclasses"
        raise NotImplementedError

    def check_field(self, model, field, message, fn=None):
        try:
            model._meta.get_field(field)
        except (FieldDoesNotExist, TypeError, AttributeError):
            if not fn or not fn(field):
                raise Http404(message)

    def get(self, request, *args, **kwargs):
        self.check_parameters(request, *args, **kwargs)
        return super(AnimeListView, self).get(request, *args, **kwargs)


class AnimeAjaxListView(AnimeListView):

    http_method_names = ['get', 'post']
    ajax_call = False

    def get_context_data(self, **kwargs):
        (link, cachestr) = self.get_link()
        cachestr = self._filter.get_cachestring(cachestr)
        context = {'link': link}
        if self.updated(cachestr):
            context.update(self.create_context_data(cachestr, link, **kwargs))
            cache.clean_cache(self.cache_name, cachestr)
            if not self.ajax_call:
                cache.update_named_cache(cachestr)
            self.data = context
            cache.cset('%s:%s' % (self.ajax_cache_name, cachestr), context, 0)
        elif self.data:
            context = self.data
        if not self.ajax_call:
            context['cachestr'] = cachestr
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

    @ajaxResponse
    def ajax(self, request, *args, **kwargs):
        if not hasattr(self, 'response_name'):
            raise NotImplementedError(_("Response name Must be defined."))
        response = {'response': self.response_name, 'status': False}
        try:
            ret = self.ajax_process(request, *args, **kwargs)
            if hasattr(self, 'fields'):
                ret['head'] = self.fields
            response.update({'status': True, 'text': ret})
        except Http404, e:
            response['text'] = e
        return response

    def ajax_process(self, request, *args, **kwargs):
        self.check_parameters(request, *args, **kwargs)
        if not hasattr(self, 'fields'):
            raise NotImplementedError(_("Fields must be defined."))
        self.object_list = self.get_queryset()
        ret = self.get_context_data(object_list=self.object_list)
        ret['list'] = [
                dict([(name, getattr(x, name)) for name in self.fields]) \
                for x in ret['list'] ]
        return ret

