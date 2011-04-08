#Some helpful functions
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote
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

def invalidateCacheKey(fragment_name, *variables):
   args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
   cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
   cache.delete(cache_key)

#All shit in one place
#TODO: fix it later
def cleanTableCache(order, status, page, user):
    link = ''
    if status >= 0:
        link += 'show/%s/' % status
    if order != AnimeItem._meta.ordering[0]:
        link += 'sort/%s/' % order
    if status >= 0:
        cachestr = '%s:%s%s' % (user.id, link, page)
    else:
        cachestr = link + str(page)
    if user.is_authenticated():
        maintablekey = 'mainTable:%s' % user.id
    else:
        maintablekey = 'mainTable'        
    maintable = cache.get(maintablekey)       
    try:
        cached = True
        if status >= 0:
            #Last exception can be thrown here 
            currenttable = maintable[status]
        else:
            currenttable = maintable
        try:
            currenttable[order].index(page)
        except KeyError:
            currenttable[order] = [page]
        except ValueError:
            currenttable[order].append(page)
        except:
            currenttable = {order: [page]}
        else:
            cached = False
        if cached:
            if status >= 0:
                #or here, lol
                maintable[status] = currenttable
                cache.delete('Pages:' + cachestr)
            else:
                maintable = currenttable
            invalidateCacheKey('mainTable', cachestr)
            cache.set(maintablekey, maintable)
    except:
        invalidateCacheKey('mainTable', cachestr)
        maintable = {status: {order:[page]}}
        cache.set(maintablekey, maintable)
    return link, cachestr