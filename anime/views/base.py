
import anime.core.base as coreMethods
from annoying.decorators import render_to
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from anime.models import AnimeItem, AnimeRequest
from anime.utils.catalog import last_record_pk, getPages, cleanRequestsCache
from random import randint


# TODO: Pager here
# wut?


@render_to('anime/list.html')
def index(request, user=None, status=None, order='title', page=0):
    if page is None:
        page = 0
    else:
        page = int(page)

    if user is None or int(user) == request.user.id:
        user = request.user
    else:
        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            raise Http404

    if order is None:
        order = 'title'
    try:
        AnimeItem._meta.get_field(order[1:] if order.startswith('-') else order)
    except:
        raise Http404

    return coreMethods.index(user, request.user.id, status, order, page)


@render_to('anime/requests.html')
def requests(request, status=None, rtype=None, page=0):
    limit = settings.REQUESTS_PAGE_LIMIT
    qs = AnimeRequest.objects.order_by("-id")
    try:
        page = int(page or request.REQUEST.get('page'))
    except:
        page = 0
    if not status:
        qs = qs.exclude(Q(status=1) | Q(status=3))
    else:
        qs = qs.filter(status=status)
    if rtype:
        qs = qs.filter(requestType=rtype)
    (link, cachestr) = cleanRequestsCache(status, rtype, page)
    pages = getPages(link, page, qs, 'id', limit)
    items = qs[page*limit:(page+1)*limit]
    return {'requests': items, 'cachestr': cachestr, 'link': link,
            'pages': pages, 'page': {'number': page, 'start': page*limit}}


@render_to('anime/search.html')
def search(request, string=None, field=None, order=None, page=0):
    string = string or request.POST.get('string') or ''
    field = field or request.POST.get('field')
    order = order or request.POST.get('sort')
    page = page or request.POST.get('page')
    response = {'cachestr': 'badsearch', 'link': 'search/', 'string': string}
    ret = coreMethods.search(field, string, order=order, page=page)
    try:
        response.update(ret)
    except ValueError:
        pass
    return response


@render_to('anime/card.html')
def card(request, anime_id=0):
    anime = None
    if not anime_id:
        anime_id = randint(0, last_record_pk(AnimeItem))
        try:
            anime_id = AnimeItem.objects.values_list('id').filter(pk__gte=anime_id)[0][0]
        except:
            return {}
        else:
            return HttpResponseRedirect(reverse('card', args=[anime_id]))
    try:
        ret = coreMethods.card(anime_id, request.user)
    except AnimeItem.DoesNotExist:
        raise Http404(_('Record not found.'))
    return ret
