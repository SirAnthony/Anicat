#Some helpful functions
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote

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
