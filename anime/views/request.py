# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from anime.models import AnimeRequest, REQUEST_TYPE, REQUEST_STATUS
from anime.views.classes import AnimeListView


class RequestsListView(AnimeListView):
    error_messages = {
        'bad_status': _('Bad status.'),
        'bad_type': _('Bad request type.'),
    }

    model = AnimeRequest
    paginate_by = settings.REQUESTS_PAGE_LIMIT
    template_name = 'anime/requests.html'
    cache_name = 'requests'
    pages_numeric = True
    parameters = [
        ('status', None, 'bad_status'),
        ('rtype', None, 'bad_type'),
        ('page', 1, 'bad_page'),
    ]

    def get_link(self):
        link = {}
        if self.status is not None:
            link['status'] = self.status
        if self.rtype is not None:
            link['rtype'] = self.rtype
        link_name = reverse('requests', kwargs=link)
        cachestr = '%s%s' % (link_name, self.page)
        link['link'] = link_name
        return link, cachestr

    def check_status(self, request, status):
        if status is not None:
            REQUEST_STATUS[int(status)]
        return status

    def check_rtype(self, request, rtype):
        if rtype is not None:
            REQUEST_TYPE[int(rtype)]
        return rtype

    def check_parameters(self, request, **kwargs):
        super(RequestsListView, self).check_parameters(request, **kwargs)
        self.order = '-id'

    def get_queryset(self):
        qs = super(RequestsListView, self).get_queryset()
        qs = qs.order_by(self.order)
        if not self.status:
            qs = qs.exclude(Q(status=1) | Q(status=3))
        else:
            qs = qs.filter(status=self.status)
        if self.rtype:
            qs = qs.filter(requestType=self.rtype)
        qs = qs.select_related('anime')
        return qs
