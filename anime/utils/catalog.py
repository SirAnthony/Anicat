#Some helpful functions
from anime.models import UserStatusBundle
from anime.utils import cache


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
