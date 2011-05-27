#Some helpful functions
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote
from django.contrib.auth.models import User
from models import AnimeItem

def getVal(val, obj = None, default = ''):
    if obj and obj.has_key(val):
        return obj[val]
    return default

def getAttr(obj, val, default = ''):
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
                s = qs.only(order)[i-1:i+1]
            pages.extend(map(lambda x: unicode(getattr(x, order)).strip()[:4], s))
        pages.append(unicode(getattr(qs.order_by('-'+order).only(order)[0], order)).strip()[:4])
        pages = [a+' - '+b for a,b in zip(pages[::2], pages[1::2])]
    return pages

def invalidateCacheKey(fragment_name, *variables):
   args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
   cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
   cache.delete(cache_key)

#All shit in one place
#TODO: fix it later
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
    maintable = cache.get(maintablekey)
    if maintable is None:
        maintable = {}
    cached = True
    if status is not None:
        try:
            currenttable = maintable[status]
        except:
            currenttable = {}
    else:
        currenttable = maintable
    try:
        currenttable[order].index(page)
    except KeyError:
        currenttable[order] = [page]
    except ValueError:
        currenttable[order].append(page)
    except Exception, e:
        currenttable = {order: [page]}
    else:
        cached = False
    if cached:
        if status is not None:
            maintable[status] = currenttable
        else:
            maintable = currenttable
        cache.delete('Pages:' + cachestr)
        invalidateCacheKey('mainTable', cachestr)
        cache.set(maintablekey, maintable)
    return link, cachestr

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