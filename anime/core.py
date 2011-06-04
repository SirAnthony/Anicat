
from anime.models import AnimeItem, EDIT_MODELS
from django.core.cache import cache
from anime.functions import createPages
from hashlib import sha1 

def search(field, string, request, attrs={}):
    #Rewrite this
    if not string:
        return {'text': 'Empty query.'}
    if not field:
        field = 'name'
    limit = attrs.get('limit', 20)
    qs = None
    link = 'search/'
    if string:
        link += string + '/'
    if field:
        link += 'field/%s/' % field
    try: #FIXME: 2 caches: /sort/title/ and /
        order = attrs.get('order')
        AnimeItem._meta.get_field(order)
        link += 'sort/%s/' % order
    except Exception:
        order = 'title'
    try:
        page = int(attrs.get('page', 0))
    except:
        page = 0
    cachestr = sha1(link + str(page)).hexdigest()
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
            qs = AnimeItem.objects.filter(animenames__title__icontains=string).distinct().order_by(order)
        else:
            return {'text': 'This field not avaliable yet.'}
        pages = createPages(qs, order, limit)
        items = qs[page*limit:(page+1)*limit]
        count = qs.count()
        cache.set('search:%s' % cachestr, {'pages': pages, 'items': items, 'count': count})
    return {'response': 'search', 'text': {'pages': pages, 'items': items,
            'count': count, 'page': page, 'link': link, 'cachestr': cachestr}}
