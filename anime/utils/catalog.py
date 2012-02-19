#Some helpful functions
from hashlib import sha1
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote
from django.contrib.auth.models import User
from anime.models import AnimeItem


def last_record_pk(model):
    try:
        return model.objects.values_list('pk').latest('pk')[0]
    except:
        return 0


def getPages(link, page, qs, order, limit):
    #TODO: use page in iterator-like pager function
    pages = cache.get('Pages:{0}'.format(link))
    if pages is None:
        pages = createPages(qs, order, limit)
        cache.set('Pages:{0}'.format(link), pages)
    return pages


def createPages(qs, order, limit=20):
    pages = []
    reverse = '-'
    count = qs.count()
    if order.startswith('-'):
        order = order[1:]
        reverse = ''
    if count > limit:
        for i in range(0, count, limit):
            if not i:
                s = (qs.only(order)[i],)
            else:
                s = qs.only(order)[i - 1:i + 1]
            pages.extend(unicode(getattr(x, order)).strip()[:4] for x in s)
        pages.append(unicode(getattr(qs.order_by(reverse + order).only(order)[0],
                            order)).strip()[:4])
        pages = [a + ' - ' + b for a, b in zip(pages[::2], pages[1::2])]
    return pages


def invalidateCacheKey(fragment_name, *variables):
    args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)

#TODO: custom formatter to this

def cleanTableCache(order, status, page, user, cuserid):
    link = '/'
    if status is not None:
        if user.id != cuserid:
            link += 'user/%s/' % user.id
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
    _cleanCache(maintablekey, status, order, page, cachestr, 'mainTable')
    return link, cachestr


def cleanRequestsCache(status, rtype, page):
    link = '/requests/'
    if status is not None:
        link += 'status/%s/' % status
    if rtype is not None:
        link += 'type/%s/' % rtype
    cachestr = link + str(page)
    _cleanCache('requests', status, rtype, page, cachestr)
    return link, cachestr


def cleanSearchCache(string, field, order, page):
    link = u'/search/'
    if string is not None:
        link += u'%s/' % string
    if field is not None:
        link += u'field/%s/' % field
    if order != u'title':
        link += u'sort/%s/' % order
    hashlink = sha1(link.encode('utf-8')).hexdigest()
    cachestr = sha1(link.encode('utf-8') + str(page)).hexdigest()
    #You can clean cache part if you know original link, i.e. never.
    if not _cleanCache('search', None, hashlink, page, cachestr):
        cache.delete('search:%s' % cachestr)
        #cache.delete('Pages:%s' % hashlink)
    return link, cachestr, hashlink


def _cleanCache(cachekey, first, second, third, cachestr, ckey=None):
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
        invalidateCacheKey(ckey or cachekey, cachestr)
        cache.set(cachekey, ccontent)
    return cached


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
