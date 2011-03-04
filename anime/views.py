#import re

from models import AnimeForm, AnimeItem, AnimeName, UserCreationFormMail, UserStatusBundle, USER_STATUS
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.cache import cache_page
from annoying.decorators import render_to
from django.contrib import auth
from functions import getVal, getAttr
from random import randint

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
    items = AnimeItem.objects.all()[page*limit:(page+1)*limit]
    statuses = UserStatusBundle.objects.get_for_user(items, request.user.id)
    return {'list': [(anime, statuses[anime.id]) for anime in items],
            'pages': pages, 'page': {'number': page, 'start': page*limit}}

#@cache_page(10)
@render_to('anime/card.html')
def card(request, animeId=0):
    if not animeId:
        animeId = randint(1, AnimeItem.objects.count())
    try:
        anime = AnimeItem.objects.get(id=int(animeId))
    except Exception:
        anime = None
    bundles = None
    if anime and anime.bundle:
        bundles = anime.bundle.animeitems.all().order_by('releasedAt')
        if request.user.is_authenticated():
            status = UserStatusBundle.objects.get_for_user(bundles, request.user.id)
            bundles = map(lambda x: (x, getAttr(status[x.id], 'status', 0)), bundles)
        else:
            bundles = map(lambda x: (x,  0), bundles)
    return {'anime': anime, 'bundles': bundles}

@ajaxResponse
def get(request):
    fields = []
    if not request.POST:
        return {'text': 'Only POST method allowed.'}
    try:
        aid = int(getVal('id', request.POST['id']))
        anime = AnimeItem.objects.get(id=aid)
    except Exception, e:
        return {'text': 'Invalid id.'  + str(e)}
    try:
        fields.extend(request.POST['field'].split(','))
    except Exception, e:
        return {'text': 'Bad request fields: ' + str(e)}
    response = {'id': aid, 'order': fields}
    for field in fields:
        #FIXME: so bad
        if field == 'state':
            if not request.user.is_authenticated():
                response[field] = 'Anonymous users has not statistics.'
                continue
            else:                
                try:
                    bundle = UserStatusBundle.objects.get(anime=anime, user=request.user)
                    status = int(bundle.status)
                except Exception:
                    status = 0
                response[field] = {'selected': status, 'select': dict(USER_STATUS)}
                if status == 2 or status == 4:
                    response[field].update({'completed': bundle.count, 'all': anime.episodesCount})
        elif field == 'name':
            #FIXME: cruve
            response[field] = map(lambda n: {'name': str(n)}, AnimeName.objects.filter(anime=anime))
        elif field == 'genre':
            response[field] = ', '.join(map(lambda n: str(n), anime.genre.all()))
        elif field == 'translation':
            response[field] = anime.translation()
        elif field == 'type':
            response[field] = anime.releaseTypeS()
        elif field == 'bundle':
            if anime.bundle:
                items = anime.bundle.animeitems.all().order_by('releasedAt')
                status = UserStatusBundle.objects.get_for_user(items, request.user.id)
                response[field] = map(lambda x: {'name': x.title, 'elemid': x.id,
                                                 'job': getAttr(getVal(x.id, None, status), 'status', 0, )},
                                      items)
        else:
            try:
                response[field] = getattr(anime, field)
            except Exception, e:
                response[field] = 'Error: ' + str(e)
    
    response = {'response': 'getok', 'text': response}
    
    return response

@ajaxResponse
def ajaxlogin(request):
    response = {}
    if not request.POST:
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already logined.'
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
    if not request.user.is_authenticated() and request.method == 'POST':
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
    elif request.user.is_authenticated():
        response['text'] = 'Already registred.'
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
            #model.save()
            return HttpResponseRedirect('/thanks/')
    ctx = {'form': form}
    ctx.update(csrf(request))
    return ctx

