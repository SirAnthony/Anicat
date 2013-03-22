
from annoying.decorators import render_to
from audit_log.models.managers import ACTION_TYPES
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from anime.models import AnimeItem, HISTORY_MODELS
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
    #fields = ['air', 'id', 'title', 'episodes', 'release', 'type']
    response_name = 'history'

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
        cachestr = u'{0}{1}'.format(link_name, self.page)
        link['link'] = link_name
        return link, cachestr

    def check_parameters(self, request, **kwargs):
        _get = lambda val, default=None: \
                kwargs.get(val) or request.POST.get(val) or default

        model = _get('model', 'anime')
        if not model in HISTORY_MODELS:
            raise Http404(self.error_messages['bad_model'])
        self.model = HISTORY_MODELS[model].audit_log.model

        status = _get('status')
        if status and status.upper() not in HISTORY_STATUSES:
            raise Http404(self.error_messages['bad_status'])

        order = _get('order', 'action_date')
        try:
            self.model._meta.get_field(
                    order[1:] if order.startswith('-') else order)
        except:
            if order not in self.ADDITIONAL_FIELDS:
                raise Http404(self.error_messages['bad_order'])


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
        qs = qs.order_by(self.order).values()
        return qs

    #~ @ajaxResponse
    #~ def ajax(self, request, *args, **kwargs):
        #~ response = {'response': 'history', 'status': False}
        #~ try:
            #~ ret = self.ajax_process(request, *args, **kwargs)
            #~ paginator = ret['pages']['items']
            #~ ret['head'] = self.fields
            #~ ret['count'] = paginator.count
            #~ ret['pages']['items'] = paginator.get_names()
            #~ response.update({'status': True, 'text': ret})
        #~ except Http404, e:
            #~ response['text'] = e
        #~ return response



@render_to('anime/history.html')
def history(request, field=None, page=0):
    Model = None
    limit = 30
    link = 'add/'
    try:
        page = int(page)
    except:
        page = 0
    if not field:
        Model = AnimeItem

    qs = Model.audit_log.filter(action_type=u'I')
    pages = qs.count()/limit + 1
    res = qs[page*limit:(page+1)*limit]
    def r(obj):
        ret = {}
        for fieldName in obj._meta.fields:
            name = fieldName.name
            ret[name] = getattr(obj, name)
            if name in ['releasedAt', 'endedAt']:
                if hasattr(ret[name], 'strftime'):
                    ret[name] = ret[name].strftime("%d.%m.%Y")
            elif name == 'action_user':
                if request.user.is_staff:
                    try:
                        ret[name] = ret[name].username
                    except AttributeError:
                        ret[name] = '*'
                else:
                    ret[name] = 'Anonymous'
            else:
                ret[name] = getattr(obj, name)
        return ret
    table = map(r, res)
    return {
        'table': table,
        'pages': range(1, pages+1),
        'link': link,
        'page': page
    }
