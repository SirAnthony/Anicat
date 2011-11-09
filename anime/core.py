# -*- coding: utf-8 -*-
from anime.models import (
            AnimeItem,
            UserStatusBundle,
            LINKS_TYPES, EDIT_MODELS, USER_STATUS,
            )
from django.core.cache import cache
from anime.functions import createPages
from anime.functions import getVal, getAttr, updateMainCaches
from hashlib import sha1


def get(request):
    fields = []
    if request.method != 'POST':
        return {'text': 'Only POST method allowed.'}
    try:
        aid = int(request.POST.get('id', 0))
        anime = AnimeItem.objects.get(id=aid)
    except Exception, e:
        return {'text': 'Invalid id.' + str(e)}
    try:
        fields.extend(request.POST.getlist('field'))
    except Exception, e:
        return {'text': 'Bad request fields: ' + str(e)}
    response = {'id': aid, 'order': fields}
    for field in fields:
        #FIXME: so bad
        try:
            model = EDIT_MODELS[field]
        except KeyError:
            model = None
        if field == 'state':
            if not request.user.is_authenticated():
                response[field] = 'Anonymous users have no statistics.'
                continue
            else:
                try:
                    bundle = model.objects.get(anime=anime, user=request.user)
                    status = int(bundle.state)
                except Exception:
                    status = 0
                response[field] = {'selected': status,
                                        'select': dict(USER_STATUS)}
                if status == 2 or status == 4:
                    response[field].update({'completed': bundle.count,
                                                'all': anime.episodesCount})
        elif field == 'name':
            #FIXME: cruve
            response[field] = list(model.objects.filter(anime=anime).values('title'))
        elif field == 'genre':
            response[field] = ', '.join(anime.genre.values_list('name', flat=True))
        elif field == 'links':
            response[field] = dict([(LINKS_TYPES[x[0]][-1], x[1]) \
                for x in model.objects.filter(anime=anime).values_list('linkType', 'link')])
        elif field == 'type':
            response[field] = anime.releaseTypeS
        elif field == 'bundle':
            if anime.bundle:
                items = anime.bundle.animeitems.all().order_by('releasedAt')
                status = UserStatusBundle.objects.get_for_user(items, request.user.id)
                response[field] = [{'name': x.title, 'elemid': x.id, 'job': getAttr(
                                                            getVal(x.id, status, None),
                                                                    'state', 0, )}
                                        for x in  items]
        else:
            try:
                response[field] = getattr(anime, field)
            except Exception, e:
                response[field] = 'Error: ' + str(e)
    r = 'card' if request.POST.get('card') else 'get'
    response = {'response': r, 'status': True, 'text': response}
    return response


def search(field, string, request, attrs={}):
    #Rewrite this
    string = string.strip()
    if not string:
        return {'text': 'Empty query.'}
    if not field:
        field = 'name'
    limit = attrs.get('limit', 20)
    try:
        limit = int(limit)
    except:
        limit = 20
    if limit > 30:
        limit = 30
    qs = None
    link = 'search/'
    if string:
        link += string + '/'
    if field:
        link += 'field/%s/' % field
    #FIXME: 2 caches: /sort/title/ and /
    try:
        order = attrs.get('order')
        AnimeItem._meta.get_field(order)
        link += 'sort/%s/' % order
    except Exception:
        order = 'title'
    try:
        page = int(attrs.get('page', 0))
    except:
        page = 0
    cachestr = sha1(link.encode('utf-8') + str(page)).hexdigest()
    cached = cache.get('search:%s' % cachestr)
    if cached:
        try:
            pages = cached['pages']
            items = cached['items']
            count = cached['count']
        except KeyError:
            cache.delete('search:%s' % cachestr)
            return {'text': 'Cache error occured. Try again.'}
    else:
        if field == 'name':
            qs = AnimeItem.objects.filter(animenames__title__icontains=string)\
                                        .distinct().order_by(order)
        else:
            return {'text': 'This field not avaliable yet.'}
        pages = createPages(qs, order, limit)
        items = qs[page * limit:(page + 1) * limit]
        count = qs.count()
        cache.set('search:%s' % cachestr, {'pages': pages, 'items': items, 'count': count})
    return {'response': 'search', 'text': {'pages': pages, 'items': items,
            'count': count, 'page': page, 'link': link, 'cachestr': cachestr}}
