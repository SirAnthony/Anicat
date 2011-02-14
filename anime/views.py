import re

from models import AnimeForm, AnimeItem
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.utils import simplejson
from annoying.decorators import render_to
from django.contrib import auth

def ajaxResponse(fn):
    ret = {'text': 'Unprocessed error', 'response': 'error'}
    def new(*args):
        ret.update(fn(*args)) #FIXME: no type check
        return HttpResponse(simplejson.dumps(ret), mimetype='application/javascript')
    return new

# TODO: Pager here
@render_to('anime/list.html')
def index(request):
    return {'list': AnimeItem.objects.all(), 'user': request.user}

@render_to('anime/view.html')
def info(request, anime_id=0):
    return {'list': AnimeItem.objects.get(id=int(anime_id))}

@ajaxResponse
def ajaxlogin(request):
    response = {}
    if not request.POST:
        response['text'] = 'Only POST method allowed.'
    else:
        username = request.POST['name']
        password = request.POST['pass']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            response.update({'response': 'logok', 'text': {'name': user.username}})
        else:
            response.update({'response': 'logfail', 'text': 'Bad username or password'})
    return response

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


@render_to('anime/add.html')
def add(request):
    form = AnimeForm()
    if request.method == 'POST':
        form = AnimeForm(request.POST, request.FILES)
        if form.is_valid():
            model = form.save(commit=False)
            #slugt = re.sub(r'[^a-z0-9\s-]', ' ', model.title)
            #slugt = re.sub(r'\s+', ' ', slugt)
            #model.slug = re.sub(r'\s', '-', slugt)
            model.save()
            return HttpResponseRedirect('/thanks/')
    ctx = {'form': form}
    ctx.update(csrf(request))
    return ctx

