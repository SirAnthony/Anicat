
from models import AnimeItem, AnimeName, UserStatusBundle, USER_STATUS
from forms import AnimeForm, UserStatusForm, UserCreationFormMail
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from annoying.decorators import render_to
from django.contrib import auth
from functions import getAttr
from random import randint



# TODO: Pager here
@render_to('anime/list.html')
def index(request, page=0):
    page = int(request.REQUEST.get('page', int(page)))
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

@render_to('anime/card.html')
def card(request, animeId=0):
    if not animeId:
        animeId = randint(1, AnimeItem.objects.count())
    try:
        anime = AnimeItem.objects.all()[animeId]
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

@render_to('anime/stat.html')
def stat(request, userId=0):
    user = None
    tuser = []
    username = 'Anonymous'
    if userId:
        try:
            user = User.objects.get(id=userId)
        except Exception, e:
            user = None
    elif request.user.is_authenticated():
        user = request.user
        username = user.username
    if user:
        total = {'name': 'Total', 'full': 0, 'count': 0, 'custom': 0}
        for status in USER_STATUS[1::]:
            arr = UserStatusBundle.objects.filter(user=user.id, status=status[0]).extra(
                select = {'full': 'SUM(anime_animeitem.episodesCount*anime_animeitem.duration)',
                          'custom': 'SUM(anime_animeitem.duration*anime_userstatusbundle.count)',
                          'count': 'COUNT(*)'}
                ).values('anime__episodesCount', 'anime__duration', 'full', 'custom',
                'count').select_related('anime__episodesCount', 'anime__duration').get()
            arr['name'] = status[1]            
            if status[0] == 3:
                arr['custom'] = arr['full']
            #FUUU
            total['full'] += arr['full'] or 0
            total['count'] += arr['count'] or 0
            total['custom'] += arr['custom'] or 0
            tuser.append(arr)
        tuser.append(total)
    return {'username': username, 'stat': tuser}

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

@render_to('anime/add.html')
def test(request):
    form = UserStatusForm()
    ctx = {'form': form}
    ctx.update(csrf(request))
    return ctx
