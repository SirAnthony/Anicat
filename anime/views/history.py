
from annoying.decorators import render_to
from audit_log.models.managers import ACTION_TYPES
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from anime.models import (AnimeItem, HISTORY_MODELS,
                            AUDIT_FIELDS, AUDIT_MODEL_FIELDS)
from anime.views.classes import AnimeAjaxListView
from anime.views.ajax import ajaxResponse


HISTORY_STATUSES = dict(ACTION_TYPES)


class HistoryListView(AnimeAjaxListView):
    error_messages = {
        'bad_order': _('Bad order.'),
        'bad_model': _('Bad model.'),
        'bad_status': _('Bad status.'),
    }

    paginate_by = settings.HISTORY_PAGE_LIMIT
    template_name = 'anime/history/history.html'
    cache_name = 'history'
    ajax_cache_name = 'ajaxhistory'
    ADDITIONAL_FIELDS = []
    response_name = 'history'
    fields = AUDIT_FIELDS

    def get_link(self):
        userid = self.kwargs.get('user_id')
        link = {}
        if self.model_name != 'anime':
            link['model'] = self.model_name
        if self.status is not None:
            link['status'] = self.status
        if self.order != 'action_date':
            link['order'] = self.order
        link_name = reverse('history', kwargs=link)
        cachestr = u'{0}:{1}{2}'.format(self.current_user.is_staff,
                                            link_name, self.page)
        link['link'] = link_name
        return link, cachestr

    def check_parameters(self, request, **kwargs):
        _get = lambda val, default=None: \
                kwargs.get(val) or request.POST.get(val) or default

        model = _get('model', 'anime')
        if not model in HISTORY_MODELS:
            raise Http404(self.error_messages['bad_model'])
        self.model = HISTORY_MODELS[model].audit_log.model

        self.fields = AUDIT_FIELDS + AUDIT_MODEL_FIELDS[model] + ('locked',)

        status = _get('status')
        if status and status.upper() not in HISTORY_STATUSES:
            raise Http404(self.error_messages['bad_status'])

        order = _get('order', '-action_date')
        order_field = order[1:] if order.startswith('-') else order
        self.check_field(self.model, order_field, self.error_messages['bad_order'],
                            lambda o: o in self.ADDITIONAL_FIELDS)

        self.model_name = model
        self.current_user = request.user
        self.order = order
        self.status = status
        self.page = _get('page', 1)
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
