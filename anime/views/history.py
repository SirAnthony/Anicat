# -*- coding: utf-8 -*-
from audit_log.models.managers import ACTION_TYPES
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from anime.models import (HISTORY_MODELS, AUDIT_FIELDS, AUDIT_MODEL_FIELDS)
from anime.views.classes import AnimeAjaxListView


HISTORY_STATUSES = dict(ACTION_TYPES)


class HistoryListView(AnimeAjaxListView):
    error_messages = {
        'bad_order': _('Bad order.'),
        'bad_model': _('Bad model.'),
        'bad_fields': _('Bad fields.'),
        'bad_status': _('Bad status.'),
        'bad_page': _('Bad page.'),
    }

    paginate_by = settings.HISTORY_PAGE_LIMIT
    pages_numeric = True
    template_name = 'anime/history/history.html'
    cache_name = 'history'
    ajax_cache_name = 'ajaxhistory'
    response_name = 'history'
    default_order = '-action_date'
    fields = AUDIT_FIELDS
    ADDITIONAL_FIELDS = []
    parameters = [
        ('model', 'anime', 'bad_model'),
        ('fields', AUDIT_FIELDS, 'bad_fields'),
        ('status', None, 'bad_status'),
        ('order', default_order, 'bad_order'),
        ('page', 1, 'bad_page'),
    ]

    def get_link(self):
        link = {}
        if self.model_name != 'anime':
            link['model'] = self.model_name
        if self.status is not None:
            link['status'] = self.status
        if self.order != self.default_order:
            link['order'] = self.order
        link['link'] = reverse('history', kwargs=link)
        return link

    def get_cachestr(self, link):
        cachestr = u'{0}:{1}'.format(self.current_user.is_staff, link['link'])
        return self.apply_filter(cachestr, self.page)

    def check_model(self, request, model):
        if not model in HISTORY_MODELS:
            raise ValueError
        return HISTORY_MODELS[model].audit_log.model

    def check_fields(self, request, fields):
        return AUDIT_FIELDS + AUDIT_MODEL_FIELDS[self.model] + ('locked',)

    def check_status(self, request, status):
        if status and status.upper() not in HISTORY_STATUSES:
            raise ValueError
        return status

    def check_parameters(self, request, **kwargs):
        super(HistoryListView, self).check_parameters(request, **kwargs)
        self.current_user = request.user
        self.kwargs['page'] = self.page

    def get_queryset(self):
        qs = super(HistoryListView, self).get_queryset()
        state = self.status
        if state:
            qs = qs.filter(action_type=state)
        qs = qs.order_by(self.order)
        if self.current_user.is_staff:
            qs = qs.select_related('action_user')
        if self.model_name != 'anime':
            qs = qs.select_related('anime')
        return qs
