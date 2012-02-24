
from django.views.generic.list import ListView
from anime.utils import cache
from anime.utils.paginator import Paginator

class AnimeListView(ListView):

    http_method_names = ['get']
    paginator_class = Paginator

    def get_context_data(self, **kwargs):
        (link, cachestr) = self.get_link()
        context = {'cachestr': cachestr, 'link': link}
        if self.updated(cachestr):
            queryset = kwargs.pop('object_list')
            page_size = self.get_paginate_by(queryset)
            context_object_name = self.get_context_object_name(queryset)
            paginator = None
            if page_size:
                paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
                paginator.set_order(self.order)
                paginator.set_cachekey(link['link'])
                context.update({
                    'pages': {'current': page.number,
                        'start': page.start_index(),
                        'items': paginator,
                    },
                    'list': queryset,
                })
            else:
                context.update({'pages': {}, 'list': queryset})
            cache.update_named_cache(cachestr)
            context.update(kwargs)
            cache.clean_cache(self.cache_name, cachestr)
            if context_object_name is not None:
                context[context_object_name] = queryset
        return context

    def updated(self, cachestr):
        if not cache.key_valid(self.cache_name, cachestr):
            return True
        return not cache.latest(self.__class__.__name__, cachestr)

    def get_link(self):
        "Implementation in subclasses"
        raise NotImplementedError

    def check_parameters(self, request, *args, **kwargs):
        "Implementation in subclasses"
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        self.check_parameters(request, *args, **kwargs)
        return super(AnimeListView, self).get(request, *args, **kwargs)



