
import anime.core as coreMethods
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_control
from annoying.decorators import render_to
from anime.models import AnimeItem, AnimeLink, UserStatusBundle, AnimeRequest, USER_STATUS
from anime.functions import getAttr, createPages, cleanTableCache, cleanRequestsCache
from random import randint


def latestStatus(request, userId=0):
    try:
        if userId:
            return UserStatusBundle.objects.filter(user=User.objects.get(id=userId)).latest("changed").changed
        return UserStatusBundle.objects.filter(user=request.user).latest("changed").changed
    except:
        return

# TODO: Pager here


@render_to('anime/list.html')
def index(request, order='title', page=0, status=None):
    try:
        page = int(page or request.REQUEST.get('page'))
    except:
        page = 0
    limit = 100
    try:
        AnimeItem._meta.get_field(order)
    except:
        order = 'title'
    qs = AnimeItem.objects.order_by(order)
    try:
        status = int(status)
        USER_STATUS[status]
        if request.user.is_authenticated():
            if status:
                ids = map(lambda x: x[0], UserStatusBundle.objects.filter(
                        user=request.user, state=status).values_list('anime'))
                qs = qs.filter(id__in=ids)
            else:
                ids = map(lambda x: x[0], UserStatusBundle.objects.filter(
                        user=request.user, state__gte=1).values_list('anime'))
                qs = qs.exclude(id__in=ids)
        else:
            raise Exception
    except:
        status = None
    (link, cachestr) = cleanTableCache(order, status, page, request.user)
    pages = cache.get('Pages:' + link)
    if not pages:
        pages = createPages(qs, order, limit)
        cache.set('Pages:%s' % link, pages)
    items = qs[page * limit:(page + 1) * limit]
    return {'list': items, 'link': link, 'cachestr': cachestr,
            'pages': pages, 'page': {'number': page, 'start': page*limit}}


@render_to('anime/requests.html')
def requests(request, status=None, rtype=None, page=0):
    limit = 30
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
    pages = cache.get('requestPages:' + link)
    if not pages:
        pages = createPages(qs, 'id', limit)
        cache.set('requestPages:%s' % link, pages)
    items = qs[page*limit:(page+1)*limit]
    return {'requests': items, 'cachestr': cachestr, 'link': link,
            'pages': pages, 'page': {'number': page, 'start': page*limit}}


@render_to('anime/search.html')
def search(request, string=None, field=None, order=None, page=0):
    limit = 20
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
        try:
            anime = AnimeItem.objects.get(id=animeId)
        except:
            return {}
        bundles = None
        names = None
        if anime:
            names = anime.animenames.values()
            if anime.bundle:
                bundles = anime.bundle.animeitems.values('id', 'title').all().order_by('releasedAt')
        try:
            links = anime.links.order_by('linkType').all()
        except AnimeLink.DoesNotExist:
            links = None
        except AttributeError:
            links = None
        ret = {'anime': anime, 'bundles': bundles, 'animelinks': links,
                'names': names}
        cache.set('card:%s' % animeId, ret)
    if request.user.is_authenticated():
        userstatus = None
        try:
            userstatus = ret['anime'].statusbundles.values('state', 'count').get(user=request.user)
        except UserStatusBundle.DoesNotExist:
            pass
        except AttributeError:
            pass
        else:
            userstatus['statusName'] = USER_STATUS[userstatus['state'] or 0][1]
        ret['userstatus'] = userstatus
    return ret


@condition(last_modified_func=latestStatus)
@render_to('anime/stat.html')
def stat(request, userId=0):
    user = None
    username = 'Anonymous'
    tuser = None
    if userId:
        try:
            user = User.objects.get(id=userId)
        except Exception, e:
            user = None
    elif request.user.is_authenticated():
        user = request.user
        username = user.username
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
    return {'username': username, 'stat': tuser}


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


@render_to('anime/history.html')
def history(request, field=None, page=0):
    Model = None
    limit = 30
    link = 'add/'
    try:
        page = int(page)
    except:
        page = 0
    if field:
       pass
    else:
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
                try:
                    ret[name] = ret[name].strftime("%d.%m.%Y")
                except:
                    pass
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
    return {'table': table, 'pages': range(1, pages+1),
            'link': link, 'page': page
    }

#@render_to('anime/add.html')


def test(request):
    ctx = {}
    return ctx
