from models import AnimeForm, AnimeItem
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

# TODO: Pager here
def index(request):
    return render_to_response('anime/list.html', {
            'list':AnimeItem.objects.all()
            })

def info(request, anime_slug=''):
    return render_to_response('anime/view.html', {
            'list':AnimeItem.objects.get(slug=anime_slug)
            })

def add(request):
    if request.method == 'POST': 
        form = ContactForm(request.POST) 
        if form.is_valid(): 
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        return render_to_response('anime/add.html', {
                'form':AnimeForm()
                })
    
