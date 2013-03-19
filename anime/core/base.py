# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from anime.core.explorer import GetError, FieldExplorer
from anime.forms.Error import FilterForm
from anime.models import AnimeItem, UserStatusBundle, USER_STATUS
from anime.utils import cache


ERROR_MESSAGES = {
    'get_data': {
        'bad_request': _('Only POST method allowed.'),
        'bad_id': _('Invalid id'),
        'bad_fields': _('Bad request fields: {0}'),
        'no_fields': _('No fields passed'),
    },
}


def get_data(request):
    fields = []
    if request.method != 'POST':
        return {'text': ERROR_MESSAGES['get_data']['bad_request']}
    try:
        aid = int(request.POST.get('id', 0))
        anime = AnimeItem.objects.get(id=aid)
    except Exception:
        return {'text': ERROR_MESSAGES['get_data']['bad_id']}
    try:
        fields.extend(request.POST.getlist('field'))
    except Exception, e:
        return {'text': ERROR_MESSAGES['get_data']['bad_fields'].format(e)}
    if not fields:
        return {'text': ERROR_MESSAGES['get_data']['no_fields']}
    response = {'order': fields}
    for field in fields:
        field_expl = FieldExplorer(field)
        try:
            response[field] = field_expl.get_value(anime, request)
        except GetError, e:
            response[field] = unicode(e)

    r = 'card' if request.POST.get('card') else 'get'
    response = {'response': r, 'status': True, 'id': aid, 'text': response}
    return response


def card(anime_id, user):
    ret = cache.get('card:{0}'.format(anime_id))
    if not ret:
        ret = {}
        try:
            anime = AnimeItem.objects.get(id=anime_id)
        except AnimeItem.DoesNotExist:
            raise
        except Exception:
            pass
        else:
            ret.update({'anime': anime, 'names': list(anime.animenames.values())})
            if anime.bundle:
                ret['bundle'] = list(anime.bundle.animeitems.values('id', 'title').order_by('releasedAt').all())
            if anime.links:
                ret['links'] = list(anime.links.order_by('linkType').values().all())
            cache.cset('card:{0}'.format(anime_id), ret)
    if user.is_authenticated() and 'anime' in ret:
        userstatus = None
        try:
            userstatus = ret['anime'].statusbundles.values('state', 'count', 'rating').get(user=user)
        except (UserStatusBundle.DoesNotExist, AttributeError):
            pass
        else:
            userstatus['statusName'] = USER_STATUS[userstatus['state'] or 0][1]
        ret['userstatus'] = userstatus
    return ret


def filter_list(request):
    form = FilterForm(data=request.POST)
    if form.is_valid():
        request.session['filter'] = dict(
                    (k, v) for k, v in form.cleaned_data.items() if v)
        cache.invalidate_key('filter', request.session.session_key)
        return {'status': True}
    return {'form': form}
