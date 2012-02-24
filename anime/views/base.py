
import anime.core.base as coreMethods
from annoying.decorators import render_to
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from anime.models import AnimeItem
from anime.utils.catalog import last_record_pk
from random import randint


@render_to('anime/search.html')
def search(request, string=None, field=None, order=None, page=0):
    string = string or request.POST.get('string') or ''
    field = field or request.POST.get('field')
    order = order or request.POST.get('sort')
    page = page or request.POST.get('page')
    response = {'cachestr': 'badsearch', 'link': 'search/', 'string': string}
    ret = coreMethods.search(field, string, order=order, page=page)
    try:
        response.update(ret)
    except ValueError:
        pass
    return response


@render_to('anime/card.html')
def card(request, anime_id=0):
    anime = None
    if not anime_id:
        anime_id = randint(0, last_record_pk(AnimeItem))
        try:
            anime_id = AnimeItem.objects.values_list('id').filter(pk__gte=anime_id)[0][0]
        except:
            return {}
        else:
            return HttpResponseRedirect(reverse('card', args=[anime_id]))
    try:
        ret = coreMethods.card(anime_id, request.user)
    except AnimeItem.DoesNotExist:
        raise Http404(_('Record not found.'))
    return ret
