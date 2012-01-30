# -*- coding: utf-8 -*-
from hashlib import sha1
from django.core.cache import cache
from anime.models import (
            AnimeItem,
            UserStatusBundle,
            LINKS_TYPES, EDIT_MODELS, USER_STATUS,
            )
from anime.utils.catalog import createPages, getVal, getAttr, updateMainCaches


class GetError(Exception):
    pass


class FieldExplorer(object):
    def __init__(self, field):
        if field == 'releasedAt,endedAt':
            field = 'release'
        self.field = field

    def get_field(self):
        field = getattr(self, self.field, None)
        return field

    def get_value(self, anime, request):
        if not anime:
            return
        field = self.get_field()
        try:
            if callable(field):
                return field(anime, request)
            else:
                return getattr(anime, self.field, None)
        except Exception, e:
            raise GetError('Error: ' + str(e))

    def get_model(self):
        try:
            model = EDIT_MODELS[self.field]
        except KeyError:
            model = None
        return model

    def state(self, anime, request):
        if not request.user.is_authenticated():
            return 'Anonymous users have no statistics.'
        try:
            bundle = self.get_model().objects.get(anime=anime, user=request.user)
            status = int(bundle.state)
        except Exception:
            status = 0
        response = {'state': status, 'select': dict(USER_STATUS)}
        # Магические числа, охуенно
        if status == 3:
            response.update({'rating': bundle.rating})
        elif status in (2, 4):
            response.update({'completed': bundle.count,
                                        'all': anime.episodesCount})
        return response

    def name(self, anime, request):
        return list(self.get_model().objects.filter(anime=anime).values_list('title', flat=True))

    def genre(self, anime, request):
        return ', '.join(anime.genre.values_list('name', flat=True))

    def links(self, anime, request):
        model = self.get_model()
        if model:
            d = {}
            for x in model.objects.filter(anime=anime).values_list('linkType', 'link'):
                for t in LINKS_TYPES:
                    if t[0] == x[0]:
                        name = t[-1]
                if name not in d:
                    d[name] = []
                d[name].append(x[1])
            return d

    def type(self, anime, request):
        return anime.releaseTypeS

    def releaseType(self, anime, request):
        return anime.releaseTypeS

    def bundle(self, anime, request):
        if anime.bundle:
            items = anime.bundle.animeitems.all().order_by('releasedAt')
            bundles = [{'name': x.title, 'elemid': x.id} for x in  items]
            return {'id': anime.bundle.id, 'bundles': bundles}
        return None


def get(request):
    fields = []
    if request.method != 'POST':
        # XXX: Антипаттерн, имя функции - get, но разрешен только пост
        return {'text': 'Only POST method allowed.'}
    try:
        aid = int(request.POST.get('id', 0))
        anime = AnimeItem.objects.get(id=aid)
    except Exception, e:
        return {'text': 'Invalid id: ' + str(e)}
    try:
        fields.extend(request.POST.getlist('field'))
    except Exception, e:
        return {'text': 'Bad request fields: ' + str(e)}
    if not fields:
        return {'text': 'No fields passed.'}
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


def search(field, string, request, attrs={}):
    #Rewrite this
    try:
        string = string.strip()
        if not string:
            raise AttributeError
    except AttributeError:
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
    link = '/search/'
    if string:
        link += string + '/'
    if field:
        link += 'field/%s/' % field
    try:
        order = attrs.get('order')
        AnimeItem._meta.get_field(order)
        if order != 'title':
            link += 'sort/%s/' % order
    except Exception:
        order = 'title'
    try:
        page = int(attrs.get('page', 0))
    except:
        page = 0
    #FIXME: Search cache lives its own life
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
