#Some helpful functions
from anime.models import UserStatusBundle
from anime.utils import cache
from django.conf import settings
from django.db import DatabaseError


def last_record_pk(model):
    try:
        return model.objects.values_list('pk').latest('pk')[0]
    except:
        return 0


def latest_status(user):
    pk = cache.get('lastuserbundle:{0}'.format(user.id))
    if not pk:
        try:
            pk = UserStatusBundle.objects.filter(user=user) \
                .values('pk').latest('changed').get('pk', None)
        except:
            pk = None
        cache.cset('lastuserbundle:{0}'.format(user.id), pk)
    return pk

def sql_concat(field, separator):
    eng = settings.DATABASES['default']['ENGINE']
    if eng == 'django.db.backends.mysql':
        ret = 'GROUP_CONCAT({0} SEPARATOR "{1}")'
    elif eng == 'django.db.backends.sqlite3':
        ret = 'GROUP_CONCAT({0}, "{1}")'
    else:
        raise DatabaseError('Bad engine.')
    return ret.format(field, separator)
