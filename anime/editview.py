
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from annoying.decorators import render_to
import anime.edit as editMethods

@render_to('anime/add.html')
def add(request):
    result = editMethods.addAnimeItem(request)
    try:
        return HttpResponseRedirect('/card/%s/' % result['id'])
    except KeyError:
            form = result['form']
    result.update(csrf(request))
    return result

@render_to('anime/edit.html')
def edit(request, itemId, model='anime', field=None):
    res = editMethods.edit(request, itemId, model, field)
    if res.get('status', None):
        if model in ['anime', 'name', 'links', 'status']:
            return HttpResponseRedirect('/card/%s/' % itemId)
        elif model == 'bundle':
            rid = res.get('id')
            if rid == None:
                rid = 0
            return HttpResponseRedirect('/edit/bundle/%s/' % rid)
    else:
        return res
