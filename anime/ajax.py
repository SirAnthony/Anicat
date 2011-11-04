
from django.http import HttpResponse
#from django.core.cache import cache
from django.utils import simplejson
from django.utils.encoding import force_unicode
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
    return response

@ajaxResponse
def change(request):
    try:
        aid = int(request.POST.get('id', 0))
    except Exception, e:
        return {'text': 'Invalid id.'  + str(e)}
    response = editMethods.edit(request, aid, request.POST.get('model', None),
                                request.POST.get('field', None),
                                request.POST.get('set', None))
    if response.has_key('form'):
        try:
            response['form'] = response['form'].as_json()
        except Exception, e:
            del response['form']
            response.update({'response': 'error', 'status': False, 'text': str(e)})
    if response['text']:
        t = response['text'].copy()
        if type(t) is dict:
            for key, value in t.iteritems():
                if not t[key]:
                    del response['text'][key]
                else:
                    response['text'][key] = force_unicode(t[key])
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
        {'page': request.POST.get('page', 0), 'order': request.POST.get('sort'),
         'limit': request.POST.get('limit', limit)}
    )
    if response.has_key('response'):
        del response['text']['link']
        del response['text']['cachestr']
        del response['text']['pages']
        items = response['text'].pop('items')
        response['text']['items'] = [{'name': x.title, 'type': x.releaseTypeS,
            'numberofep': x.episodesCount, 'id': x.id, 'release': x.release,
            'air': x.air } for x in items]
    response['status'] = True
    return response
