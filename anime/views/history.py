
from anime.models import AnimeItem
from annoying.decorators import render_to


@render_to('anime/history.html')
def history(request, field=None, page=0):
    Model = None
    limit = 30
    link = 'add/'
    try:
        page = int(page)
    except:
        page = 0
    if field:
       pass
    else:
        Model = AnimeItem

    qs = Model.audit_log.filter(action_type=u'I')
    pages = qs.count()/limit + 1
    res = qs[page*limit:(page+1)*limit]
    def r(obj):
        ret = {}
        for fieldName in obj._meta.fields:
            name = fieldName.name
            ret[name] = getattr(obj, name)
            if name in ['releasedAt', 'endedAt']:
                try:
                    ret[name] = ret[name].strftime("%d.%m.%Y")
                except:
                    pass
            elif name == 'action_user':
                if request.user.is_staff:
                    try:
                        ret[name] = ret[name].username
                    except AttributeError:
                        ret[name] = '*'
                else:
                    ret[name] = 'Anonymous'
            else:
                ret[name] = getattr(obj, name)
        return ret
    table = map(r, res)
    return {
        'table': table,
        'pages': range(1, pages+1),
        'link': link,
        'page': page
    }
