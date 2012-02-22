
from datetime import datetime
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from anime.models import ( AnimeBundle, AnimeItem, AnimeName,
                            UserStatusBundle, AnimeRequest)


ERROR_MESSAGES = {
    'bad_item_type': _('Bad item type passed: {0}')
}


ITEM_TYPES = {

}

def latest(t, date, pks={}):
    '''Return True if date is greater than last_change
    pks is {'item type': 'item pk'} dict for using records caches
    instead of model's cache.
    '''
    return  get_latest(t, pks) < date


def get_latest(itemtype, pks={}):
    '''Return  last changed date for item type.'''
    if not itemtype in ITEM_TYPES:
        raise ValueError(ERROR_MESSAGES['bad_item_type'].format(itemtype))
    return max([get_item_latest(x, pks.get(x.__name__)) \
                    for x in ITEM_TYPES[itemtype]])


def get_item_latest(t, pk=None):
    return get_named_cache(get_cache_name(t, pk))


def get_cache_name(t, pk=None):
    if not isinstance(t, type):
        key = str(t.pk) if t.pk else ''
        name = t.__class__.__name__
    else:
        key = str(pk) if pk else ''
        name = t.__name__
    if key:
        return '{0}:{1}'.format(name, key)
    return name


def update_cache(t, pk=None):
    return update_named_cache(get_cache_name(t, pk))


def get_named_cache(name):
    return cache.get(name) or update_named_cache(name)


def update_named_cache(name):
    date = datetime.now()
    cache.set(name, date)
    return date


def update_cache_on_save(sender, instance, signal, *args, **kwargs):
    update_cache(instance)
    update_cache(instance.__class__)
