
from anime.models import AnimeItem, EDIT_MODELS


def search(field, string, request, attrs={}):
    if not string:
        return {'text': 'Empty query.'}
    if not field:
        field = 'name'
    qs = None
    try:
        order = attrs.get('order')
        AnimeItem._meta.get_field(order)
    except Exception:
        order = 'title'
    try:
        page = int(attrs.get('page', 0))
    except:
        page = 0
    if field == 'name':
        qs = AnimeItem.objects.filter(animenames__title__icontains=string).distinct()
    else:
        return {'text': 'This field not avaliable yet.'}
    return {'response': 'search', 'text': {'items': qs.order_by(order), 'page': page}}
