# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from anime.core.explorer import GetError, FieldExplorer
from anime.models import AnimeItem, AnimeLink, UserStatusBundle, USER_STATUS
from anime.utils.catalog import ( getPages, createPages,
                updateMainCaches, cleanTableCache, cleanSearchCache)


ERROR_MESSAGES = {
    'get_data': {
        'bad_request': _('Only POST method allowed.'),
        'bad_id': _('Invalid id'),
        'bad_fields': _('Bad request fields: {0}'),
        'no_fields': _('No fields passed'),
    },
    'search': {
        'empty': _('Empty query.'),
        'bad_field': _('This field not avaliable yet.'),
        'cache_error': _('Cache error occured. Try again.'),
    }
}


def get_data(request):
    fields = []
    if request.method != 'POST':
        return {'text': ERROR_MESSAGES['get_data']['bad_request']}
    try:
        aid = int(request.POST.get('id', 0))
        anime = AnimeItem.objects.get(id=aid)
    except Exception:
        return {'text': ERROR_MESSAGES['get_data']['bad_id']}
    try:
        fields.extend(request.POST.getlist('field'))
    except Exception, e:
        return {'text': ERROR_MESSAGES['get_data']['bad_fields'].format(e)}
    if not fields:
        return {'text': ERROR_MESSAGES['get_data']['no_fields']}
    response = {'order': fields}
    for field in fields:
        field_expl = FieldExplorer(field)
        try:
            response[field] = field_expl.get_value(anime, request)
        except GetError, e:
            response[field] = e.message

    r = 'card' if request.POST.get('card') else 'get'
    response = {'response': r, 'status': True, 'id': aid, 'text': response}
    return response


def index(user, user_id, status, order, page):
    limit = settings.INDEX_PAGE_LIMIT
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
    (link, cachestr) = cleanTableCache(order, status, page, user, user_id)
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
                'user': None if user_id == user.id else user.id,
                'status': status
            },
            'pages': pages, 'page': {'number': page, 'start': page*limit}}


def search(field, string, **kwargs):
    #Rewrite this
    ret = {
        'count': 0,
        'items': [],
        'pages': {'current': 0, 'items': []}
    }

    try:
        string = string.strip()
        if not string:
            raise AttributeError
    except AttributeError:
        return ERROR_MESSAGES['search']['empty']
    if not field:
        field = 'name'
    elif field != 'name':
        return ERROR_MESSAGES['search']['bad_field']
    try:
        limit = kwargs.get('limit', settings.SEARCH_PAGE_LIMIT)
        limit = int(limit)
        if limit > 30:
            limit = 30
    except:
        limit = settings.SEARCH_PAGE_LIMIT
    try:
        page = int(kwargs.get('page', 0))
    except:
        page = 0
    try:
        order = attrs.get('order')
        AnimeItem._meta.get_field(order)
    except Exception:
        order = 'title'

    (link, cachestr, hashlink) = cleanSearchCache(string, field, order, page)
    cached = cache.get('search:%s' % cachestr)
    if cached:
        try:
            ret.update(cached)
        except KeyError:
            cache.delete('search:%s' % cachestr)
            return ERROR_MESSAGES['search']['cache_error']
    else:
        qs = None
        if field == 'name':
            qs = AnimeItem.objects.filter(animenames__title__icontains=string)\
                                        .distinct().order_by(order)
        pages = getPages(hashlink, page, qs, order, limit)
        ret.update({'count': qs.count(),
            'items': qs[page * limit:(page + 1) * limit],
            'pages': {'current': page,
                      'start': page * limit, 'items': pages}
        })
        cache.set('search:%s' % cachestr, ret)
    ret.update({'link': link, 'cachestr': cachestr})
    return ret


def card(anime_id, user):
    ret = cache.get('card:%s' % anime_id)
    if not ret:
        ret = {}
        try:
            anime = AnimeItem.objects.get(id=anime_id)
        except AnimeItem.DoesNotExist:
            raise
        except Exception:
            pass
        else:
            ret.update({'anime': anime, 'names': anime.animenames.values()})
            if anime.bundle:
                ret['bundle'] = anime.bundle.animeitems.values('id', 'title').all().order_by('releasedAt')
            if anime.links:
                ret['links'] = anime.links.order_by('linkType').all()
            cache.set('card:%s' % anime_id, ret)
    if user.is_authenticated() and 'anime' in ret:
        userstatus = None
        try:
            userstatus = ret['anime'].statusbundles.values('state', 'count', 'rating').get(user=user)
        except (UserStatusBundle.DoesNotExist, AttributeError):
            pass
        else:
            userstatus['statusName'] = USER_STATUS[userstatus['state'] or 0][1]
        ret['userstatus'] = userstatus
    return ret
