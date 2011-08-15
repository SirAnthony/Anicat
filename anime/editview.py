
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from annoying.decorators import render_to
import anime.edit as editMethods

@render_to('anime/edit.html')
def add(request):
    res = editMethods.edit(request)
    if res.get('status', None):
        rid = res.get('id')
        return HttpResponseRedirect('/card/%s/' % (rid or 0))
    res.update(csrf(request))
    return res

@render_to('anime/request.html')
def request_item(request, requestId):
    form = editMethods.edit(request, requestId, 'request')
    return form

@render_to('anime/edit.html')
def feedback(request):
    res = editMethods.edit(request, 0, 'feedback')
    if res.get('status', None):
        rid = res.get('id')
        return HttpResponseRedirect('/request/%s/' % (rid or 0))
    res.update(csrf(request))
    return res

@render_to('anime/edit.html')
def anime_request(request):
    res = editMethods.edit(request, 0, 'animerequest')
    if res.get('status', None):
        rid = res.get('id')
        return HttpResponseRedirect('/request/%s/' % (rid or 0))
    res.update(csrf(request))
    return res

@render_to('anime/edit.html')
def edit(request, itemId, model='anime', field=None):
    res = editMethods.edit(request, itemId, model, field)
    if res.get('status', None):
        rid = res.get('id')
        if model == 'bundle':
            return HttpResponseRedirect('/edit/bundle/%s/' % (rid or 0))
        else:
            return HttpResponseRedirect('/card/%s/' % (rid or 0))
    else:
        return res
