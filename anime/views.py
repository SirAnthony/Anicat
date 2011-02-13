import re

from models import AnimeForm, AnimeItem
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import csrf_protect


def ajax(fn):
    ret = {'text': 'Not processed error', 'response': 'error'}
    def new(*args):
        ret.update(fn(*args)) #FIXME: no type check
        return HttpResponse(simplejson.dumps(ret), mimetype='application/javascript')
    return new

# TODO: Pager here
def index(request):
    return render_to_response('anime/list.html', {
            'list':AnimeItem.objects.all()
            }, context_instance = RequestContext(request))

def info(request, anime_id=0):
    return render_to_response('anime/view.html', {
            'list':AnimeItem.objects.get(id=int(anime_id))
            }, context_instance = RequestContext(request))

@ajax
def ajaxlogin(request):
    response = {}
    if not request.POST:
        response['text'] = 'Only POST method allowed.'
    else:
        pass

def add(request):
    form = AnimeForm()
    #if request.method == 'POST':
        #form = AnimeForm(request.POST, request.FILES)
        #if form.is_valid():
            #model = form.save(commit=False)
            #slugt = re.sub(r'[^a-z0-9\s-]', ' ', model.title)
            #slugt = re.sub(r'\s+', ' ', slugt)
            #model.slug = re.sub(r'\s', '-', slugt)
            #model.save()
            #return HttpResponseRedirect('/thanks/')

    #ctx = {'form': form}
    #ctx.update(csrf(request))
    return render_to_response(
        'anime/add.html',
        ctx, context_instance = RequestContext(request))

