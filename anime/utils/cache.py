
from datetime import datetime
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote
from anime.forms.json import is_iterator
from anime.models import ( AnimeBundle, AnimeItem, AnimeName,
                            UserStatusBundle, AnimeRequest)


ERROR_MESSAGES = {
    'bad_item_type': 'Bad item type passed: {0}'
}


ITEM_TYPES = {
    'IndexListView': [AnimeItem],
    'RequestsListView': [AnimeRequest],
}


def latest(t, cachestr, keys={}):
    '''Return True if date is greater than last_change
    pks is {'item type': 'item pk'} dict for using records caches
    instead of model's cache.
    '''
    date = cache.get(cachestr)
    if not date:
        update_named_cache(cachestr)
        return False
    return get_latest(t, keys) < date


def get_latest(itemtype, keys={}):
    '''Return  last changed date for item type.'''
    if not itemtype in ITEM_TYPES:
        raise ValueError(ERROR_MESSAGES['bad_item_type'].format(itemtype))
    names = []
    for x in ITEM_TYPES[itemtype]:
        name = get_cache_name(x, keys.get(x.__name__))
        names.extend(name if type(name) is list else [name])
    c = get_named_cache(names)
    if type(c) is datetime:
        return c
    elif type(c) is dict:
        c = c.values()
    return max(c)


def get_cache_name(t, pk=None):
    if is_iterator(pk):
        return [get_cache_name(t, x) for x in pk]
    if not isinstance(t, type):
        key = str(t.pk) if t.pk else ''
        name = t.__class__.__name__
    else:
        key = str(pk) if pk else ''
        name = t.__name__
    if key:
        return '{0}:{1}'.format(name, key)
    return name


def get_named_cache(name):
    if type(name) in (list, tuple):
        c = cache.get_many(name)
    else:
        c = cache.get(name)
    return c or update_named_cache(name)


def update_named_cache(name):
    date = datetime.now()
    if type(name) in (list, tuple):
        c = cache.set_many(dict([(x, date) for x in name]), 0)
    else:
        cache.set(name, date, 0)
    return date


def get_cache(name):
    return cache.get(name)


def set_cache(name, data):
    return cache.set(name, data, 0)


def update_cache(t, pk=None):
    return update_named_cache(get_cache_name(t, pk))


def update_cache_on_save(sender, instance, signal, *args, **kwargs):
    update_cache(instance)
    update_cache(instance.__class__)


def clean_cache(name, cachestr):
    invalidate_key(name, cachestr)


def key_valid(fragment_name, *variables):
    args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    return cache.has_key(cache_key)


def invalidate_key(fragment_name, *variables):
    args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)
