#import re

from models import AnimeForm, AnimeItem, UserCreationFormMail
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.cache import cache_page
from annoying.decorators import render_to
from django.contrib import auth
from functions import getVal

def ajaxResponse(fn):
    ret = {'text': 'Unprocessed error', 'response': 'error'}
    def new(*args):
        ret.update(fn(*args)) #FIXME: no type check
        return HttpResponse(simplejson.dumps(ret), mimetype='application/javascript')
    return new

# TODO: Pager here
@render_to('anime/list.html')
def index(request, page=0):
    page = int(getVal('page', int(page), request.REQUEST))
    limit = 100
    pages = []
    for i in range(0, AnimeItem.objects.count(), 100):
        s = AnimeItem.objects.only('title')[i:i+2]
        pages.extend(map(lambda x: x.title.strip()[:3], s))
    pages.append(AnimeItem.objects.order_by('-title').only('title')[0].title.strip()[:3])
    pages = pages[1:]
    pages = [a+' - '+b for a,b in zip(pages[::2], pages[1::2])]
    return {'list': 
            AnimeItem.objects.all().select_related('statusbundles')[page*limit:(page+1)*limit],
            'pages': pages, 'page': {'number': page, 'start': page*limit}}

@cache_page(10)
@render_to('anime/view.html')
def card(request, anime_id=0):
    return {'list': AnimeItem.objects.get(id=int(anime_id))}

@ajaxResponse
def get(request):
    if not request.POST:
        return {'text': 'Only POST method allowed.'}
    response = {}
    return response

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
    return HttpResponseRedirect("/")

@render_to('anime/register.html')
def register(request):
    if request.method == 'POST':
        form = UserCreationFormMail(request.POST)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=user.username, password=form.data['password1'])
            auth.login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = UserCreationFormMail()
    return {'form': form}

@ajaxResponse
def ajaxregister(request):
    response = {}
    if not request.POST:
        response['text'] = 'Only POST method allowed.'
    else:
        form = UserCreationFormMail(request.POST)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=user.username, password=form.data['password1'])
            auth.login(request, user)
            response.update({'response': 'logok', 'text': {'name': user.username}})
        else:
            response.update({'response': 'regfail', 'text': form.errors})
    return response

@render_to('anime/changes.html')
def changes(request):
    return {}

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

