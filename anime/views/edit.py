# -*- coding: utf-8 -*-
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from annoying.decorators import render_to
import anime.edit as editMethods


@render_to('anime/edit.html')
def add(request):
    res = editMethods.edit(request)
    if res.get('status', None):
        rid = res.get('id') or 0
        return HttpResponseRedirect(reverse('card', args=[rid]))
    res.update(csrf(request))
    return res


@render_to('anime/request.html')
def request_item(request, request_id):
    form = editMethods.edit(request, request_id, 'request')
    return form


@render_to('anime/edit.html')
def feedback(request):
    res = editMethods.edit(request, 0, 'feedback')
    if res.get('status', None):
        rid = res.get('id') or 0
        return HttpResponseRedirect(reverse('request_item', args=[rid]))
    res.update(csrf(request))
    return res


@render_to('anime/edit.html')
def anime_request(request):
    res = editMethods.edit(request, 0, 'animerequest')
    if res.get('status', None):
        rid = res.get('id') or 0
        return HttpResponseRedirect(reverse('request_item', args=[rid]))
    res.update(csrf(request))
    return res


@render_to('anime/edit.html')
def edit(request, item_id, model='anime', field=None):
    res = editMethods.edit(request, item_id, model, field)
    if res.get('status', None):
        rid = res.get('id') or 0
        if model == 'bundle':
            return HttpResponseRedirect(reverse('edit_item',
                kwargs={'model': 'bundle', 'item_id': rid}))
        elif model == 'image':
            return HttpResponseRedirect(reverse('request_item', args=[rid]))
        else:
            return HttpResponseRedirect(reverse('card', args=[rid]))
    else:
        return res
