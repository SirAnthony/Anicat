
from django.http import HttpResponse
from django.core.cache import cache
from django.utils import simplejson
from anime.functions import getVal, getAttr, updateMainCaches
from anime.models import AnimeItem, AnimeName, AnimeLinks, UserStatusBundle, USER_STATUS
import anime.core as coreMethods
import anime.edit as editMethods
import anime.user as userMethods
#from datetime import datetime

def ajaxResponse(fn):
    def new(*args):
        ret = {'text': 'Unprocessed error', 'response': 'error'}
        ret.update(fn(*args)) #FIXME: no type check
        return HttpResponse(simplejson.dumps(ret), mimetype='application/javascript')
    return new

@ajaxResponse
def get(request):
    response = coreMethods.get(request)
    #fields = []
    #if request.method != 'POST':
    #    return {'text': 'Only POST method allowed.'}
    #try:
    #    aid = int(request.POST.get('id', 0))
    #    anime = AnimeItem.objects.get(id=aid)
    #except Exception, e:
    #    return {'text': 'Invalid id.'  + str(e)}
    #try:
    #    fields.extend(request.POST.getlist('field'))
    #except Exception, e:
    #    return {'text': 'Bad request fields: ' + str(e)}
    #response = {'id': aid, 'order': fields}
    #for field in fields:
        #FIXME: so bad
    #    if field == 'state':
    #        if not request.user.is_authenticated():
    #            response[field] = 'Anonymous users have no statistics.'
    #            continue
    #        else:
    #            try:
    #                bundle = UserStatusBundle.objects.get(anime=anime, user=request.user)
    #                status = int(bundle.status)
    #            except Exception:
    #                status = 0
    #            response[field] = {'selected': status, 'select': dict(USER_STATUS)}
    #            if status == 2 or status == 4:
    #                response[field].update({'completed': bundle.count, 'all': anime.episodesCount})
    #    elif field == 'name':
            #FIXME: cruve
    #        response[field] = map(lambda n: {'name': str(n)}, AnimeName.objects.filter(anime=anime))
    #    elif field == 'genre':
    #        response[field] = ', '.join(map(lambda n: str(n), anime.genre.all()))
    #    elif field == 'links':
    #        try:
    #            response[field] = AnimeLinks.objects.filter(anime=anime).values('AniDB','ANN', 'MAL')[0]
    #        except:
    #            pass
    #    elif field == 'type':
    #        response[field] = anime.releaseTypeS
    #    elif field == 'bundle':
    #        if anime.bundle:
    #            items = anime.bundle.animeitems.all().order_by('releasedAt')
    #            status = UserStatusBundle.objects.get_for_user(items, request.user.id)
    #            response[field] = map(lambda x: {'name': x.title, 'elemid': x.id,
    #                                             'job': getAttr(getVal(x.id, status, None), 'status', 0, )},
    #                                  items)
    #    else:
    #        try:
    #            response[field] = getattr(anime, field)
    #        except Exception, e:
    #            response[field] = 'Error: ' + str(e)
    #response = {'response': 'getok', 'text': response}
    #if (datetime.now() - request.user.date_joined).days > 20:
    #    response['edt'] = True

    return response

@ajaxResponse
def change(request):
    try:
        aid = int(request.POST.get('id', 0))
    except Exception, e:
        return {'text': 'Invalid id.'  + str(e)}
    response = editMethods.edit(request, aid, request.POST.get('model', None), request.POST.get('fields', None))
    if response.has_key('form'):
        if response.get('status', None): #logged
            del response['form']
        else:
            try:
                response['form'] = response['form'].as_json()
            except:
                del response['form']
    return response

@ajaxResponse
def add(request):
    result = editMethods.edit(request)
    if result.get('status', None):
        return {'response': 'add', 'status': True, 'text': result.get('id', 0)}
    try:
        text = result['form'].errors
    except KeyError:
        text = None
    if not text:
        text = {'__all__': [result['text']]}
    return {'response': 'add', 'status': False, 'text': text}

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
    res = userMethods.register(request)
    if res.has_key('response'): #logged
        return {'response': 'login', 'status': True, 'text': res['text']}
    else:
        return {'response': 'regfail', 'text': res['form'].errors}

@ajaxResponse
def search(request):
    if request.method != 'POST':
        return {'text': 'Only POST method allowed.'}
    limit = 20
    response = coreMethods.search(request.POST.get('field', 'name'), 
        request.POST.get('string'), request,
        {'page': request.POST.get('page', 0), 'order': request.POST.get('sort')}
    )
    if response.has_key('response'):
        del response['text']['link']
        del response['text']['cachestr']
        del response['text']['pages']
        items = response['text'].pop('items')
        response['text']['items'] = [{'name': x.title, 'type': x.releaseTypeS,
            'numberofep': x.episodesCount, 'id': x.id, 'translation': x.translation,
            'air': x.air } for x in items]
    response['status'] = True
    return response