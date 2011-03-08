
from models import AnimeItem, AnimeName, UserStatusBundle, USER_STATUS
from forms import AnimeForm, UserStatusForm, UserCreationFormMail
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.utils import simplejson
from django.views.decorators.cache import cache_page
from django.contrib import auth
from functions import getVal, getAttr

def ajaxResponse(fn):
    ret = {'text': 'Unprocessed error', 'response': 'error'}
    def new(*args):
        ret.update(fn(*args)) #FIXME: no type check
        return HttpResponse(simplejson.dumps(ret), mimetype='application/javascript')
    return new

@ajaxResponse
def get(request):
    fields = []
    if not request.POST:
        return {'text': 'Only POST method allowed.'}
    try:
        aid = int(request.POST.get('id', 0))
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
    if not request.POST:
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
        form = UserStatusForm(request.POST, instance=obj)
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
def login(request):
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

@ajaxResponse
def register(request):
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