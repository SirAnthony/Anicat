# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponse
from django.utils.encoding import force_unicode
import anime.core.base as coreMethods
import anime.core.user as userMethods
import anime.edit as editMethods
from anime.forms.json import FormSerializer
from anime.utils.json import simplejson, prepare_data, JSONFunctionEncoder


def ajaxResponse(fn):
    def new(*args):
        ret = {'text': 'Unprocessed error', 'response': 'error'}
        #FIXME: no type check
        ret.update(fn(*args))
        for key in ret.copy():
            if ret[key] is None:
                del ret[key]
        ret = prepare_data(ret)
        return HttpResponse(simplejson.dumps(ret, cls=JSONFunctionEncoder),
                mimetype='application/javascript')
    return new


def extract_errors(r):
    return getattr(r.get('form'), 'errors', None) \
            or {'__all__': [r.get('text')]}


@ajaxResponse
def get(request):
    return coreMethods.get_data(request)


@ajaxResponse
def change(request):
    response = editMethods.edit(request, request.POST.get('id', 0),
                                request.POST.get('model', None),
                                request.POST.get('field', None))
    return process_edit_response(response)


@ajaxResponse
def afilter(request):
    result = coreMethods.filter_list(request)
    if result.get('status', None):
        return {'response': 'filter', 'status': True, 'text': None}
    return {'response': 'filter', 'status': False, 'text': extract_errors(result)}



@ajaxResponse
def form(request):
    response = editMethods.edit(request, request.POST.get('id', 0),
                                request.POST.get('model', None),
                                request.POST.get('field', None), True)
    return process_edit_response(response)


def process_edit_response(response):
    if 'form' in response:
        if 'status' in response and not response['status']:
            del response['form']
        else:
            try:
                response['form'] = FormSerializer(response['form'])
            except Exception, e:
                del response['form']
                response.update({'response': 'error',
                    'status': False, 'text': unicode(e)})
    return response


@ajaxResponse
def add(request):
    result = editMethods.edit(request)
    if result.get('status', None):
        return {'response': 'add', 'status': True, 'id': result.get('id', 0), 'text': None}
    return {'response': 'add', 'status': False, 'text': extract_errors(result)}


@ajaxResponse
def login(request):
    res = userMethods.login(request)
    if res.get('response', False):
        return {'response': 'login', 'status': True, 'text': res.get('text')}
    return {'response': 'login', 'status': False, 'text': extract_errors(res)}


@ajaxResponse
def register(request):
    res = userMethods.register(request)
    if res.get('response', False):
        return {'response': 'login', 'status': True, 'text': res.get('text')}
    return {'response': 'register', 'status': False, 'text': extract_errors(res)}


@ajaxResponse
def statistics(request):
    try:
        res = userMethods.get_statistics(request)
    except Http404, e:
        return {'response': 'stat', 'status': False, 'text': e}
    return {'response': 'stat', 'status': True, 'text': res}
