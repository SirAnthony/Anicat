
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from hashlib import sha1

from anime.models import ( AnimeItem, AnimeRequest, UserStatusBundle,
                           USER_STATUS, REQUEST_TYPE, REQUEST_STATUS )
from anime.views.classes import AnimeListView


class IndexListView(AnimeListView):
    error_messages = {
        'bad_user': _('User does not exist.'),
        'bad_order': _('Bad order.'),
    }

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
                raise Http404(self.error_messages['bad_user'])

        if order is None:
            order = 'title'
        try:
            AnimeItem._meta.get_field(order[1:] if order.startswith('-') else order)
        except:
            raise Http404(self.error_messages['bad_order'])

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
        if self.status is not None:
            #FIXME: Now userstatus lives its own life.
            cname = 'userstatus:{0}:{1}'.format(self.user.id, self.status)
            ub = cache.get(cname)
            if not ub:
                cache.set(cname, 0)
                return True
        return super(IndexListView, self).updated(cachestr)



class RequestsListView(AnimeListView):
    error_messages = {
        'bad_status': _('Bad status.'),
        'bad_type': _('Bad request type.'),
    }

    model = AnimeRequest
    paginate_by = settings.REQUESTS_PAGE_LIMIT
    template_name = 'anime/requests.html'
    cache_name = 'requests'

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

    def check_parameters(self, request, status=None, rtype=None, page=0):
        try:
            if status is not None:
                REQUEST_STATUS[int(status)]
        except:
            raise Http404(self.error_messages['bad_status'])
        try:
            if rtype is not None:
                REQUEST_TYPE[int(rtype)]
        except:
            raise Http404(self.error_messages['bad_type'])

        self.status = status
        self.rtype = rtype
        self.order = '-id'
        self.page = page or self.request.GET.get('page') or 1

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


class SearchListView(AnimeListView):
    error_messages = {
        'empty': _('Empty query.'),
        'bad_field': _('This field not avaliable yet.'),
        'bad_order': _('Bad order.'),
        'cache_error': _('Cache error occured. Try again.'),
    }

    http_method_names = ['get', 'post']
    model = AnimeItem
    paginate_by = settings.SEARCH_PAGE_LIMIT
    template_name = 'anime/search.html'
    cache_name = 'search'
    ajax = False

    def get_link(self):
        link = {}
        string = None
        if self.string is not None:
            string = self.string
            link['string'] = sha1(string.encode('utf-8')).hexdigest()
        if self.field is not None and self.field != 'name':
            link['field'] = self.field
        if self.order != u'title':
            link['order'] = self.order
        hashed_link_name = reverse('search', kwargs=link)
        cachestr = '%s%s' % (hashed_link_name, self.page)
        if string:
            link['string'] = string
            link['link'] = reverse('search', kwargs=link)
        else:
            link['link'] = hashed_link_name
        return link, cachestr

    def check_parameters(self, request, string=None, field=None,
                                        order=None, page=0):
        try:
            string = string or request.POST.get('string') or ''
            string = string.strip()
            if not string:
                raise AttributeError
        except AttributeError:
            if request.path != reverse('search'):
                raise ValueError(self.error_messages['empty'])

        field = field or request.POST.get('field') or 'name'
        if not field or field != 'name':
            raise ValueError(self.error_messages['bad_field'])

        try:
            order = order or request.POST.get('sort') or 'title'
            AnimeItem._meta.get_field(order[1:] if order.startswith('-') else order)
        except Exception:
            raise ValueError(self.error_messages['bad_order'])

        self.string = string
        self.field = field
        self.order = order
        self.page = page or request.POST.get('page') or 1

    def get_queryset(self):
        qs = super(SearchListView, self).get_queryset()
        qs = qs.order_by(self.order)
        if self.field == 'name':
            qs = qs.filter(animenames__title__icontains=self.string).distinct()
        return qs

    def get(self, request, *args, **kwargs):
        try:
            self.check_parameters(request, *args, **kwargs)
        except ValueError, e:
            raise Http404(e)
        return super(SearchListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.ajax:
            return self.get(request, *args, **kwargs)

