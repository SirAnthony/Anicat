
from models import AnimeItem, AnimeName, UserStatusBundle, USER_STATUS
from forms import AnimeForm, UserStatusForm, UserCreationFormMail
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_control
from annoying.decorators import render_to
from django.contrib import auth
from functions import getAttr, invalidateCacheKey
from random import randint
from datetime import datetime

def latestStatus(request, userId=0):
    try:
        if userId:
            return UserStatusBundle.objects.filter(user=User.objects.get(id=userId)).latest("changed").changed
        return UserStatusBundle.objects.filter(user=request.user).latest("changed").changed
    except:
        return

# TODO: Pager here
@render_to('anime/list.html')
def index(request, order='title', page=0, status=None):
    try:
        page = int(page)
    except:
        page = 0
    page = int(request.REQUEST.get('page', page))
    limit = 100
    link = ''
    
    try:
        AnimeItem._meta.get_field(order)
    except Exception:
        order = 'title'
    qs = AnimeItem.objects.order_by(order)
    try:
        status = int(status)
        USER_STATUS[status]
        if request.user.is_authenticated():
            if status:
                ids = map(lambda x: x[0], UserStatusBundle.objects.filter(
                        user=request.user, status=status).values_list('anime'))
                qs = qs.filter(id__in=ids)
            else:
                ids = map(lambda x: x[0], UserStatusBundle.objects.filter(
                        user=request.user, status__gte=1).values_list('anime'))
                qs = qs.exclude(id__in=ids)
        else:
            raise Exception
    except Exception:
        status = None
    if status >= 0:
        link += 'show/%s/' % status
    if order != AnimeItem._meta.ordering[0]:
        link += 'sort/%s/' % order
    if status >= 0:
        cachestr = '%s:%s%s' % (request.user.id, link, page)
        stat = cache.get('User:%s' % request.user.id)
        try:
            stat['updated'].remove(status)
        except Exception, e:
            pass
        else:
            cache.set('User:%s' % request.user.id, stat)
            invalidateCacheKey('mainTable', cachestr)
            cache.delete('Pages:' + cachestr)
    else:
        cachestr = link + str(page)
    pages = cache.get('Pages:' + cachestr)
    if not pages:
        pages = []
        for i in range(0, qs.count(), limit):
            if not i:
                s = (qs.only(order)[i],)
            else:
                s = qs.only(order)[i-1:i+1]
            pages.extend(map(lambda x: unicode(getattr(x, order)).strip()[:4], s))
        pages.append(unicode(getattr(AnimeItem.objects.order_by('-'+order).only(order)[0], order)).strip()[:4])
        pages = [a+' - '+b for a,b in zip(pages[::2], pages[1::2])]
        cache.set('Pages:%s' % cachestr, pages)
    items = qs[page*limit:(page+1)*limit]
    return {'list': items, 'link': link, 'cachestr': cachestr,
            'pages': pages, 'page': {'number': page, 'start': page*limit}}

@render_to('anime/card.html')
def card(request, animeId=0):
    anime = None
    if not animeId:
        animeId = randint(1, AnimeItem.objects.count())
        try:
            anime = AnimeItem.objects.all()[animeId]
        except:
            pass
    else:
        try:
            anime = AnimeItem.objects.get(id=animeId)
        except:
            pass
    bundles = None
    if anime and anime.bundle:
        bundles = anime.bundle.animeitems.all().order_by('releasedAt')
        if request.user.is_authenticated():
            status = UserStatusBundle.objects.get_for_user(bundles, request.user.id)
            bundles = map(lambda x: (x, getAttr(status[x.id], 'status', 0)), bundles)
        else:
            bundles = map(lambda x: (x,  0), bundles)
    return {'anime': anime, 'bundles': bundles}

@condition(last_modified_func=latestStatus)
@render_to('anime/stat.html')
def stat(request, userId=0):
    user = None
    username = 'Anonymous'
    tuser = None
    if userId:
        try:
            user = User.objects.get(id=userId)
        except Exception, e:
            user = None
    elif request.user.is_authenticated():
        user = request.user
        username = user.username
    if user:
        tuser = cache.get('Stat:%s' % user.id)
        if not tuser:
            tuser = []
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
            cache.set('Stat:%s' % user.id, tuser)
    return {'username': username, 'stat': tuser}

#FIXME: Do normal page if fail
def login(request):
    response = {}
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already logined.'
    else:
        username = request.POST.get('name', None)
        password = request.POST.get('pass', None)
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            response.update({'response': 'logok', 'text': {'name': user.username}})
        else:
            response.update({'response': 'logfail', 'text': 'Bad username or password'})
    return HttpResponseRedirect("/")

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

@render_to('anime/register.html')
def register(request):
    if not request.user.is_authenticated() and request.method == 'POST':
        form = UserCreationFormMail(request.POST)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=user.username, password=form.cleaned_data['password1'])
            auth.login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = UserCreationFormMail()
    return {'form': form}

@render_to('anime/changes.html')
def changes(request):
    return {}

@cache_control(private=True, no_cache=True)
#@condition(last_modified_func=latestStatus)
@render_to('anime/user.css', 'text/css')
def generateCss(request):
    styles = cache.get('userCss:%s' % request.user.id)
    if not styles:
        styles = [[] for i in range(0,len(USER_STATUS))]
        if request.user.is_authenticated():
            statuses = UserStatusBundle.objects.filter(user=request.user).exclude(status=0).values('anime','status')
            for status in statuses:
                styles[status['status']].append(str(status['anime']))
            styles = [[',.r'.join(style), ',.a'.join(style)] for style in styles]
        cache.set('userCss:%s' % request.user.id, styles)
    return {'style': styles}

@condition(last_modified_func=latestStatus)
@render_to('anime/blank.html', 'text/css')
def blank(request):
    return {}

@render_to('anime/add.html')
def add(request):
    form = AnimeForm()
    if request.method == 'POST' and request.user.is_authenticated():
        form = AnimeForm(request.POST, request.FILES)
        if form.is_valid():
            if (datetime.now() - request.user.date_joined).days < 20:
                form.addError("You cannot doing this now")
            else:
                try:
                    model = form.save(commit=False)
                    #slugt = re.sub(r'[^a-z0-9\s-]', ' ', model.title)
                    #slugt = re.sub(r'\s+', ' ', slugt)
                    #model.slug = re.sub(r'\s', '-', slugt)
                    model.save()
                    name = AnimeName(title=model.title, anime=model)
                    name.save()
                    cache.clear() #Dirty, but work
                    return HttpResponseRedirect('/')
                except Exception, e:
                    form.addError("Error %s has occured. Please make sure that the addition was successful." % e)
    ctx = {'form': form}
    ctx.update(csrf(request))
    return ctx

def updateUserCaches():
    for id in map(lambda x: x[0], User.objects.all().values_list('id')):
        pass

#@render_to('anime/add.html')
def test(request):
    #form = UserStatusForm()
    #ctx = {'form': form}
    #ctx.update(csrf(request))
    return ctx
