
import anime.core as coreMethods
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_control
from annoying.decorators import render_to
from anime.models import AnimeItem, AnimeLink, UserStatusBundle, AnimeRequest, USER_STATUS
from anime.utils.catalog import getPages, cleanTableCache, cleanRequestsCache
from random import randint


def latestStatus(request, userId=0):
    try:
        if userId:
            return UserStatusBundle.objects.filter(user=User.objects.get(id=userId)).latest("changed").changed
        return UserStatusBundle.objects.filter(user=request.user).latest("changed").changed
    except:
        return

# TODO: Pager here
# wut?


@render_to('anime/list.html')
def index(request, order='title', page=0, status=None, user=None):
    try:
        page = int(page or request.REQUEST.get('page'))
    except:
        page = 0
    limit = settings.INDEX_PAGE_LIMIT

    if user is None or int(user) == request.user.id:
        user = request.user
    else:
        try:
            user = User.objects.get(id=user)
        except:
            raise Http404

    if order is None:
        order = 'title'
    try:
        AnimeItem._meta.get_field(order[1:] if order.startswith('-') else order)
    except:
        raise Http404

    qs = AnimeItem.objects.order_by(order)
    sbundle = None
    try:
        status = int(status)
        USER_STATUS[status]
        if user.is_authenticated():
            #Fixme: 2 useless queries when cached.
            if status:
                sbundle = UserStatusBundle.objects.filter(user=user, state=status)
                ids = map(lambda x: x[0], sbundle.values_list('anime'))
                qs = qs.filter(id__in=ids)
                sbundle = sbundle.values('anime', 'count', 'rating')
            else:
                ids = map(lambda x: x[0], UserStatusBundle.objects.filter(
                        user=user, state__gte=1).values_list('anime'))
                qs = qs.exclude(id__in=ids)
        else:
            raise Exception
    except:
        status = None
    (link, cachestr) = cleanTableCache(order, status, page, user, request.user.id)
    pages = getPages(link, page, qs, order, limit)
    items = qs[page * limit:(page + 1) * limit]
    if sbundle is not None:
        ids = list(qs.values_list('id', flat=True)[page * limit:(page + 1) * limit])
        sbundle = dict(map(lambda x: (x['anime'], x), list(sbundle.filter(anime__in=ids))))
        for item in items:
            if item.id in sbundle:
                item.rating = sbundle[item.id]['rating']
                item.count = sbundle[item.id]['count']
    return {'list': items, 'cachestr': cachestr,
            'link': {
                'link': link,
                'order': order,
                'user': None if user is request.user else user.id,
                'status': status
            },
            'pages': pages, 'page': {'number': page, 'start': page*limit}}


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
    limit = settings.SEARCH_PAGE_LIMIT
    string = string or request.POST.get('string') or ''
    field = field or request.POST.get('field')
    order = order or request.POST.get('sort')
    ret = {'cachestr': 'badsearch', 'link': 'search/', 'string': string}
    response = coreMethods.search(field, string, request, {
                    'page': page or request.POST.get('page'), 'order': order})
    if response.has_key('response'):
        ret.update(response['text'])
        page = ret['page']
        ret['page'] = {'number': page, 'start': page*limit}
    else:
        ret['page'] = {'number': 0, 'start': 0}
    return ret


@render_to('anime/card.html')
def card(request, animeId=0):
    anime = None
    if not animeId:
        animeId = randint(1, AnimeItem.objects.count())
        try:
            anime = AnimeItem.objects.all()[animeId]
            #TODO: Think about:
            #animeId = AnimeItem.objects.order_by('?')[0].id
        #except IndexError:
        except:
            return {}
        else:
            #fixme double job
            return HttpResponseRedirect('/card/%s/' % animeId)
    ret = cache.get('card:%s' % animeId)
    if not ret:
        ret = {}
        try:
            anime = AnimeItem.objects.get(id=animeId)
        except:
            #TODO: return 404
            pass
        else:
            ret.update({'anime': anime, 'names': anime.animenames.values()})
            if anime.bundle:
                ret['bundles'] = anime.bundle.animeitems.values('id', 'title').all().order_by('releasedAt')
            try:
                ret['animelinks'] = anime.links.order_by('linkType').all()
            except (AnimeLink.DoesNotExist, AttributeError):
                pass
            cache.set('card:%s' % animeId, ret)
    if request.user.is_authenticated() and 'anime' in ret:
        userstatus = None
        try:
            userstatus = ret['anime'].statusbundles.values('state', 'count', 'rating').get(user=request.user)
        except (UserStatusBundle.DoesNotExist, AttributeError):
            pass
        else:
            userstatus['statusName'] = USER_STATUS[userstatus['state'] or 0][1]
        ret['userstatus'] = userstatus
    return ret


@condition(last_modified_func=latestStatus)
@render_to('anime/stat.html')
def stat(request, userId=0):
    user = None
    tuser = None
    if userId:
        try:
            user = User.objects.get(id=userId)
        except Exception, e:
            #TODO: return 404?
            user = None
    elif request.user.is_authenticated():
        user = request.user
    if user:
        tuser = cache.get('Stat:%s' % user.id)
        if not tuser:
            tuser = []
            total = {'name': 'Total', 'full': 0, 'count': 0, 'custom': 0}
            for status in USER_STATUS[1::]:
                arr = UserStatusBundle.objects.filter(user=user.id, state=status[0]).extra(
                    select = {'full': 'SUM(anime_animeitem.episodesCount*anime_animeitem.duration)',
                              'custom': 'SUM(anime_animeitem.duration*anime_userstatusbundle.count)',
                              'count': 'COUNT(*)'}
                    ).values('anime__episodesCount', 'anime__duration', 'full', 'custom',
                    'count').select_related('anime__episodesCount', 'anime__duration').get()
                arr['name'] = status[1]
                if status[0] == 3:
                    arr['custom'] = arr['full']
                #FUUU
                total['full'] += arr['full'] or 0
                total['count'] += arr['count'] or 0
                total['custom'] += arr['custom'] or 0
                tuser.append(arr)
            tuser.append(total)
            cache.set('Stat:%s' % user.id, tuser)
    return {'userid': getattr(user, 'id', None), 'stat': tuser}


@cache_control(private=True, no_cache=True)
@condition(last_modified_func=latestStatus)
@render_to('anime/user.css', 'text/css')
def generateCss(request):
    styles = cache.get('userCss:%s' % request.user.id)
    if not styles:
        styles = [[] for i in range(0,len(USER_STATUS))]
        if request.user.is_authenticated():
            statuses = UserStatusBundle.objects.filter(user=request.user).exclude(state=0).values('anime','state')
            for status in statuses:
                styles[status['state']].append(str(status['anime']))
            styles = [[',.r'.join(style), ',.a'.join(style), ',.s'.join(style)] for style in styles]
        cache.set('userCss:%s' % request.user.id, styles)
    return {'style': styles}


@condition(last_modified_func=latestStatus)
@render_to('anime/blank.html', 'text/css')
def blank(request):
    return {}


def test(request):
    ctx = {}
    return ctx
