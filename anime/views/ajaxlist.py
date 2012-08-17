
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from hashlib import sha1

from anime.models import AnimeItem
from anime.views.classes import AnimeAjaxListView
from anime.views.ajax import ajaxResponse


class SearchListView(AnimeAjaxListView):
    error_messages = {
        'empty': _('Empty query.'),
        'bad_fields': _('Fields parameter incorrect.'),
        'bad_order': _('Bad order.'),
        'bad_limit': _('Limit parameter is invalid.'),
        'cache_error': _('Cache error occured. Try again.'),
    }

    model = AnimeItem
    paginate_by = settings.SEARCH_PAGE_LIMIT
    template_name = 'anime/search.html'
    cache_name = 'search'
    ajax_cache_name = 'ajaxsearch'


    def get_link(self):
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
        cachestr = '%s%s' % (hashed_link_name, self.page)
        if self.fields:
            cachestr = sha1(cachestr + str(self.fields)).hexdigest()
        if string:
            link['string'] = string
            link['link'] = reverse('search', kwargs=link)
        else:
            link['link'] = hashed_link_name
        return link, cachestr

    def check_parameters(self, request, **kwargs):
        try:
            string = kwargs.get('string') or request.POST.get('string') or ''
            if request.method == 'GET':
                string = string.replace('+', ' ')
            string = string.strip()
            if not string:
                raise AttributeError
        except AttributeError:
            raise Http404(self.error_messages['empty'])

        fields = request.POST.getlist('fields', None) or []
        try:
            for f in fields:
                if f not in ['genre_name', 'type', 'release']:
                    self.model._meta.get_field(f)
            fields.sort()
        except (FieldDoesNotExist, TypeError, AttributeError):
            raise Exception
            raise Http404(self.error_messages['bad_fields'])

        try:
            order = kwargs.get('order') or request.POST.get('sort') or 'title'
            AnimeItem._meta.get_field(order[1:] if order.startswith('-') else order)
        except Exception:
            raise Http404(self.error_messages['bad_order'])

        try:
            self.paginate_by = int(kwargs.get('limit') or request.POST.get('limit') \
                        or settings.SEARCH_PAGE_LIMIT)
            if not 3 < self.paginate_by < settings.SEARCH_PAGE_LIMIT:
                self.paginate_by = settings.SEARCH_PAGE_LIMIT
        except:
            raise Http404(self.error_messages['bad_limit'])

        self.string = string
        self.fields = fields
        self.order = order
        self.page = kwargs.get('page') or request.POST.get('page') or 1
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

    @ajaxResponse
    def ajax(self, request, *args, **kwargs):
        response = {'response': 'search', 'status': False}
        try:
            self.check_parameters(request, *args, **kwargs)
            self.object_list = self.get_queryset()
            ret = self.get_context_data(object_list=self.object_list)
            fields = self.fields
            if not fields:
                fields = ['title', 'type', 'episodes', 'id', 'release', 'air']
            ret['list'] = [
                    dict([(name, getattr(x, name)) for name in fields]) \
                    for x in ret['list'] ]
            paginator = ret['pages']['items']
            ret['count'] = paginator.count
            ret['pages']['items'] = paginator.page_range
            response.update({'status': True, 'text': ret})
        except Http404, e:
            response['text'] = e
        return response
