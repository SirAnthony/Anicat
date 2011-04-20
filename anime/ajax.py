
from anime.models import AnimeItem, AnimeName, UserStatusBundle, USER_STATUS
from anime.forms import UserStatusForm, UserCreationFormMail
from anime.edit import _addAnimeItem
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.core.cache import cache
from django.utils import simplejson
from django.views.decorators.cache import cache_page
from django.contrib import auth
from functions import getVal, getAttr, updateMainCaches
from datetime import datetime
import anime.user as userMethods

def ajaxResponse(fn):    
    def new(*args):
        ret = {'text': 'Unprocessed error', 'response': 'error'}
        ret.update(fn(*args)) #FIXME: no type check
        return HttpResponse(simplejson.dumps(ret), mimetype='application/javascript')
    return new

@ajaxResponse
def get(request):
    fields = []
    if request.method != 'POST':
        return {'text': 'Only POST method allowed.'}
    try:
        aid = int(request.POST.get('id', 0))
        anime = AnimeItem.objects.get(id=aid)
    except Exception, e:
        return {'text': 'Invalid id.'  + str(e)}
    try:
        fields.extend(request.POST.getlist('field'))
    except Exception, e:
        return {'text': 'Bad request fields: ' + str(e)}
    response = {'id': aid, 'order': fields}
    for field in fields:
        #FIXME: so bad
        if field == 'state':
            if not request.user.is_authenticated():
                response[field] = 'Anonymous users have no statistics.'
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
                                                 'job': getAttr(getVal(x.id, status, None), 'status', 0, )},
                                      items)
        else:
            try:
                response[field] = getattr(anime, field)
            except Exception, e:
                response[field] = 'Error: ' + str(e)

    response = {'response': 'getok', 'text': response}

    return response

@ajaxResponse
def change(request):
    response = {}
    if request.method != 'POST':
        return {'text': 'Only POST method allowed.'}
    elif not request.user.is_authenticated():
        return {'text': 'You must be logged in.'}
    try:
        aid = int(request.POST.get('id', 0))
        anime = AnimeItem.objects.get(id=aid)
    except Exception, e:
        return {'text': 'Invalid id.'  + str(e)}
    try:
        field = request.POST['field']
    except Exception, e:
        return {'text': 'Bad request fields: ' + str(e)}
    response = {'id': aid, 'field': field}
    form = None
    obj = None
    if field == 'status':
        try:
            obj = UserStatusBundle.objects.get(user=request.user, anime=anime)
        except UserStatusBundle.DoesNotExist:
            obj = UserStatusBundle(user=request.user, anime=anime, status=0)
        oldstatus = obj.status
        form = UserStatusForm(request.POST, instance=obj)
        try:
            status = int(request.POST.get('status'))
        except:
            status = 0
        stat = cache.get('mainTable:%s' % request.user.id)
        for s in [status, oldstatus]:
            try:
                stat[s] = {}
            except:
                pass
        cache.set('mainTable:%s' % request.user.id, stat)
        cache.delete('userCss:%s' % request.user.id)
        cache.delete('Stat:%s' % request.user.id)
    if form:
        if form.is_valid():
            for fieldname in form.cleaned_data:
                setattr(obj, fieldname, form.cleaned_data[fieldname])
            obj.save()
            response.update({'response': 'editok', 'text': form.cleaned_data})
        else:
            response['text'] = form.errors
    else:
        response['text'] = 'Null form error.'

    return response

@ajaxResponse
def add(request):
    if request.method != 'POST':
        return {'text': 'Only POST method allowed.'}
    elif not request.user.is_authenticated():
        return {'text': 'You must be logged in.'}
    result = _addAnimeItem(request)
    try:
        return {'response': 'add', 'status': 'ok', 'text': result['id']}
    except KeyError:
        return {'response': 'add', 'status': 'fail', 'text': result['form'].errors}


@ajaxResponse
def login(request):
    res = userMethods.login(request)
    if res.has_key('response') and res['response']: #logged
        form = res['form']
        return {'response': 'login', 'status': True, 'text': {'name': form.get_user().username}}
    else:
        return {'response': 'login', 'status': False, 'text': res['form'].errors}

@ajaxResponse
def register(request):
    response = {}
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already registred.'
    else:
        form = UserCreationFormMail(request.POST)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=user.username, password=form.cleaned_data['password1'])
            auth.login(request, user)
            response.update({'response': 'logok', 'text': {'name': user.username}})
        else:
            response.update({'response': 'regfail', 'text': form.errors})
    return response

@ajaxResponse
def search(request):
    if request.method != 'POST':
        return {'text': 'Only POST method allowed.'}
    string = request.POST.get('string')
    if not string:
        return {'text': 'Empty query.'}
    response = {}
    limit = 20
    field = request.POST.get('field', 'name')
    qs = None
    try:
        order = request.POST.get('sort')
        AnimeItem._meta.get_field(order)
    except Exception:
        order = 'title'
    try:
        page = int(request.POST.get('page', 0))
    except:
        page = 0
    if field == 'name':
        qs = AnimeItem.objects.filter(animenames__title__icontains=string).distinct()
    else:
        return {'text': 'This field not avaliable yet.'}
    res = qs.order_by(order)[page*limit:(page+1)*limit]
    #FUUUUUUSHENKIFUFU
    items = [{'name': x.title, 'type': x.releaseTypeS(), 'numberofep': x.episodesCount,
             'id': x.id, 'translation': x.translation(), 'air': x.air} for x in res]
    response = {'text': {'items': items, 'page': page,
                'count': qs.count()}, 'response': 'search'}
    return response