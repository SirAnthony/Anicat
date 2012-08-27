
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from hashlib import sha1

from anime.models import AnimeItem, UserStatusBundle, USER_STATUS
from anime.utils import cache
from anime.views.classes import AnimeAjaxListView
from anime.views.ajax import ajaxResponse


class IndexListView(AnimeAjaxListView):
    error_messages = {
        'bad_user': _('User does not exist.'),
        'bad_order': _('Bad order.'),
    }

    model = AnimeItem
    paginate_by = settings.INDEX_PAGE_LIMIT
    template_name = 'anime/base/list.html'
    cache_name = 'mainTable'
    ajax_cache_name = 'ajaxlist'
    ADDITIONAL_FIELDS = ['rating', '-rating', 'changed', '-changed']

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

    def check_parameters(self, request, **kwargs):
        _get = lambda val, default=None: \
                kwargs.get(val) or request.POST.get(val) or default
        user = _get('user')
        if user is None or int(user) == request.user.id:
            user = request.user
        else:
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise Http404(self.error_messages['bad_user'])

        try:
            status = int(_get('status'))
            USER_STATUS[status]
            if not user.is_authenticated():
                raise Exception
        except:
            status = None

        order = _get('order', 'title')
        try:
            AnimeItem._meta.get_field(order[1:] if order.startswith('-') else order)
        except:
            if not status or order not in self.ADDITIONAL_FIELDS:
                raise Http404(self.error_messages['bad_order'])

        self.user = user
        self.current_user = request.user
        self.order = order
        self.status = status
        self.page = _get('page', 1)

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
        pk = cache.get('lastuserbundle:{0}'.format(self.user.id))
        if not pk and self.user.is_authenticated():
            try:
                pk = UserStatusBundle.objects.filter(user=self.user) \
                    .values('pk').latest('changed').get('pk', None)
            except:
                pk = None
            cache.cset('lastuserbundle:{0}'.format(self.user.id), pk)
        return super(IndexListView, self).updated(cachestr, {'UserStatusBundle': pk})

    @ajaxResponse
    def ajax(self, request, *args, **kwargs):
        response = {'response': 'list', 'status': False}
        try:
            self.check_parameters(request, *args, **kwargs)
            self.object_list = self.get_queryset()
            ret = self.get_context_data(object_list=self.object_list)
            fields = ['air', 'id', 'title', 'episodes', 'release', 'type']
            ret['list'] = [
                    dict([(name, getattr(x, name)) for name in fields]) \
                    for x in ret['list'] ]
            paginator = ret['pages']['items']
            ret['head'] = fields
            ret['count'] = paginator.count
            ret['pages']['items'] = paginator.get_names()
            response.update({'status': True, 'text': ret})
        except Http404, e:
            response['text'] = e
        return response


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
    template_name = 'anime/base/search.html'
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
        _get = lambda val, default=None: \
            kwargs.get(val) or request.POST.get(val) or default

        try:
            string = _get('string', '')
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
            order = _get('order', 'title')
            AnimeItem._meta.get_field(order[1:] if order.startswith('-') else order)
        except Exception:
            raise Http404(self.error_messages['bad_order'])

        try:
            self.paginate_by = int(_get('limit', settings.SEARCH_PAGE_LIMIT))
            if not 3 < self.paginate_by < settings.SEARCH_PAGE_LIMIT:
                self.paginate_by = settings.SEARCH_PAGE_LIMIT
        except:
            raise Http404(self.error_messages['bad_limit'])

        self.string = string
        self.fields = fields
        self.order = order
        self.page = _get('page', 1)
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
