
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic.list import ListView
from anime.models import AnimeItem, UserStatusBundle, USER_STATUS
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


class IndexListView(AnimeListView):

    model = AnimeItem
    paginate_by = settings.INDEX_PAGE_LIMIT
    template_name = 'anime/list.html'
    cache_name = 'mainTable'

    def get_link(self):
        userid = self.kwargs.get('user_id')

        link = {}
        if self.status is not None:
            if self.user != self.current_user:
                link['user'] = self.user.id
            link['status'] = self.status
        if self.order != self.model._meta.ordering[0]:
            link['order'] = self.order
        link_name = reverse('index', kwargs=link)
        if self.status is not None:
            cachestr = u'%s:%s%s' % (self.user.id, link_name, self.page)
        else:
            cachestr = u'%s%s' % (link_name, self.page)
        link['link'] = link_name
        return link, cachestr

    def check_parameters(self, request, user=None, status=None,
                                        order='title', page=1):
        if user is None or int(user) == request.user.id:
            user = request.user
        else:
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise Http404(_('User does not exist.'))

        if order is None:
            order = 'title'
        try:
            AnimeItem._meta.get_field(order[1:] if order.startswith('-') else order)
        except:
            raise Http404(_('Bad ordering.'))

        try:
            status = int(status)
            USER_STATUS[status]
            if not user.is_authenticated():
                raise Exception
        except:
            status = None

        self.user = user
        self.current_user = request.user
        self.order = order
        self.status = status
        self.page = page or self.request.GET.get('page') or 1

    def get_queryset(self):
        qs = super(IndexListView, self).get_queryset()
        qs = qs.order_by(self.order)
        user = self.user
        state = self.status
        if state is not None:
            if state:
                qs = qs.filter( statusbundles__user=user,
                                statusbundles__state=state
                    ).extra(select={
                        'count': 'anime_userstatusbundle.count',
                        'rating': 'anime_userstatusbundle.rating'
                    })
            else:
                qs = qs.exclude(statusbundles__user=user,
                                statusbundles__state__gte=1)
        return qs


    def updated(self, cachestr):
        if not cache.key_valid(self.cache_name, cachestr):
            return True
        if self.status is not None:
            #FIXME: Now userstatus lives its own life.
            cname = 'userstatus:{0}:{1}'.format(self.user.id, self.status)
            ub = cache.get_cache(cname)
            if not ub:
                cache.update_named_cache(cname)
                return True
        return not cache.latest(self.__class__.__name__, cachestr)
