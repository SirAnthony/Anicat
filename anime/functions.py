#Some helpful functions
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote
from django.contrib.auth.models import User
from models import AnimeItem


def getVal(val, obj=None, default=''):
    if obj and val in obj:
        return obj[val]
    return default


def getAttr(obj, val, default=''):
    try:
        return getattr(obj, val)
    except AttributeError:
        return default


def createPages(qs, order, limit=20):
    pages = []
    count = qs.count()
    if count > limit:
        for i in range(0, count, limit):
            if not i:
                s = (qs.only(order)[i],)
            else:
                s = qs.only(order)[i - 1:i + 1]
            pages.extend(unicode(getattr(x, order)).strip()[:4] for x in s)
        pages.append(unicode(getattr(qs.order_by('-' + order).only(order)[0],
                            order)).strip()[:4])
        pages = [a + ' - ' + b for a, b in zip(pages[::2], pages[1::2])]
    return pages


def invalidateCacheKey(fragment_name, *variables):
    args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)


def cleanTableCache(order, status, page, user):
    link = ''
    if status is not None:
        link += 'show/%s/' % status
    if order != AnimeItem._meta.ordering[0]:
        link += 'sort/%s/' % order
    if status is not None:
        cachestr = '%s:%s%s' % (user.id, link, page)
    else:
        cachestr = link + str(page)
    if status is not None and user.is_authenticated():
        maintablekey = 'mainTable:%s' % user.id
    else:
        maintablekey = 'mainTable'
    _cleanCache(maintablekey, status, order,
            page, cachestr, 'Pages', 'mainTable')
    return link, cachestr


def cleanRequestsCache(status, rtype, page):
    link = ''
    if status is not None:
        link += 'status/%s/' % status
    if rtype is not None:
        link += 'type/%s/' % rtype
    cachestr = link + str(page)
    _cleanCache('requests', status, rtype, page, cachestr, 'requestPages')
    return link, cachestr


def _cleanCache(cachekey, first, second, third, cachestr, pagekey, ckey=None):
    #cache = {first: {second: [third,]]}} or {second: [third,]]}
    ccontent = cache.get(cachekey)
    if ccontent is None:
        ccontent = {}
    cached = False
    if first is not None:
        try:
            firstcontent = ccontent[first]
        except KeyError:
            firstcontent = {}
    else:
        firstcontent = ccontent
    try:
        firstcontent[second].index(third)
    except KeyError:
        firstcontent[second] = [third]
    except ValueError:
        firstcontent[second].append(third)
    except Exception, e:
        firstcontent = {second: [third]}
    else:
        cached = True
    if not cached:
        if first is not None:
            ccontent[first] = firstcontent
        else:
            ccontent = firstcontent
        cache.delete('%s:%s' % (pagekey, cachestr))
        invalidateCacheKey(ckey or cachekey, cachestr)
        cache.set(cachekey, ccontent)


def updateMainCaches(status=None):
    for id in map(lambda x: x[0], User.objects.all().values_list('id')):
        t = {}
        if status is not None:
            t = cache.get('mainTable:%s' % id)
            try:
                t[status] = {}
            except:
                t = {}
        cache.set('mainTable:%s' % id, t)
    cache.set('mainTable', {})


def updateCardCache(rid):
    invalidateCacheKey('card', rid)
