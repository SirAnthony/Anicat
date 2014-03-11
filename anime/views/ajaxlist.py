# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from hashlib import sha1

from anime.models import AnimeItem
from anime.utils.catalog import latest_status
from anime.views.classes import AnimeAjaxListView


class IndexListView(AnimeAjaxListView):
    error_messages = {
        'bad_user': _('User does not exist.'),
        'bad_status': _('Bad status.'),
        'bad_order': _('Bad order.'),
        'bad_page': _('Bad page.'),
    }

    model = AnimeItem
    paginate_by = settings.INDEX_PAGE_LIMIT
    template_name = 'anime/base/list.html'
    cache_name = 'mainTable'
    ajax_cache_name = 'ajaxlist'
    response_name = 'list'
    fields = ['air', 'id', 'title', 'episodes', 'release', 'type']
    ADDITIONAL_FIELDS = ['rating', '-rating', 'changed', '-changed']
    parameters = [
        ('user', None, 'bad_user'),
        ('status', None, 'bad_status'),
        ('order', 'title', 'bad_order'),
        ('page', 1, 'bad_page')
    ]

    def get_link(self):
        link = {}
        if self.status is not None:
            if self.user != self.current_user:
                link['user'] = self.user.id
            link['status'] = self.status
        if self.order != self.model._meta.ordering[0]:
            link['order'] = self.order
        link_name = reverse('index', kwargs=link)
        if self.status is not None:
            cachestr = u'{0}:{1}{2}'.format(self.user.id, link_name, self.page)
        else:
            cachestr = u'{0}{1}'.format(link_name, self.page)
        link['link'] = link_name
        return link, cachestr

    def check_additional(self, field):
        return self.status and field in self.ADDITIONAL_FIELDS

    def check_parameters(self, request, **kwargs):
        super(IndexListView, self).check_parameters(request, **kwargs)
        self.current_user = request.user
        self.kwargs['page'] = self.page

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
                        'rating': 'anime_userstatusbundle.rating',
                        'changed': 'anime_userstatusbundle.changed',
                    })
            else:
                qs = qs.exclude(statusbundles__user=user,
                                statusbundles__state__gte=1)
        return qs

    def updated(self, cachestr):
        if not self.user.is_authenticated():
            pk = None
        else:
            pk = latest_status(self.user)
        return super(IndexListView, self).updated(cachestr,
                                    {'UserStatusBundle': pk})


class SearchListView(AnimeAjaxListView):
    error_messages = {
        'empty': _('Empty query.'),
        'bad_fields': _('Fields parameter incorrect.'),
        'bad_order': _('Bad order.'),
        'bad_limit': _('Limit parameter is invalid.'),
        'cache_error': _('Cache error occured. Try again.'),
        'bad_page': _('Bad page.'),
    }

    model = AnimeItem
    paginate_by = settings.SEARCH_PAGE_LIMIT
    template_name = 'anime/base/search.html'
    cache_name = 'search'
    ajax_cache_name = 'ajaxsearch'
    response_name = 'search'
    fields = ['air', 'id', 'title', 'episodes', 'release', 'type']
    trusted_fields = ['episodes', 'genre_name', 'type', 'release']
    parameters = [
        ('string', '', 'empty'),
        ('order', 'title', 'bad_order'),
        ('fields', fields, 'bad_fields'),
        ('limit', settings.SEARCH_PAGE_LIMIT, 'bad_limit'),
        ('page', 1, 'bad_page')
    ]

    def get_link(self):
        # FIXME: rewrite this
        link = {}
        string = None
        if self.string is not None:
            string = self.string
            link['string'] = sha1(string.encode('utf-8')).hexdigest()
        if self.order != u'title':
            link['order'] = self.order
        if self.paginate_by != settings.SEARCH_PAGE_LIMIT:
            link['limit'] = self.paginate_by
        hashed_link_name = reverse('search', kwargs=link)
        cachestr = u'{0}{1}'.format(hashed_link_name, self.page)
        if self.fields:
            cachestr = sha1(cachestr + str(self.fields)).hexdigest()
        if string:
            link['string'] = string
            link['link'] = reverse('search', kwargs=link)
        else:
            link['link'] = hashed_link_name
        return link, cachestr

    def check_fields(self, request, fields):
        fields = request.POST.getlist('fields') or self.fields
        tfields = self.trusted_fields
        for field in fields:
            if field not in tfields:
                self.check_field(self.model, field)
        return fields

    def check_limit(self, request, limit):
        limit = int(limit)
        if not 3 < limit < settings.SEARCH_PAGE_LIMIT:
            limit = settings.SEARCH_PAGE_LIMIT
        return limit

    def check_parameters(self, request, **kwargs):
        super(SearchListView, self).check_parameters(request, **kwargs)
        self.paginate_by = self.limit
        self.kwargs['page'] = self.page

    def get_queryset(self):
        if not self.string:
            return AnimeItem.objects.none()
        qs = super(SearchListView, self).get_queryset()
        qs = qs.order_by(self.order)
        qs = qs.filter(animenames__title__icontains=self.string).distinct()
        #~ if self.fields:
            #~ qs = qs.values('id', *fields)
        return qs

    def get(self, request, *args, **kwargs):
        #bad
        if request.path == reverse('search') and request.method == 'GET':
            return self.render_to_response({'cachestr': ''})
        self.check_parameters(request, *args, **kwargs)
        return super(SearchListView, self).get(request, *args, **kwargs)
