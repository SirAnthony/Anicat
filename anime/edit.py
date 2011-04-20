
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from anime.forms import AnimeForm
from anime.models import AnimeName, USER_STATUS
from anime.functions import updateMainCaches
from annoying.decorators import render_to
from datetime import datetime

def _addAnimeItem(request):
    form = AnimeForm(request.POST, request.FILES)
    ret = {'form': form}
    if form.is_valid():
        if (datetime.now() - request.user.date_joined).days < 20:
            form.addError("You cannot doing this now")
        else:
            try:
                model = form.save(commit=False)
                model.title = model.title.strip()
                model.save()
                form.save_m2m()
                name = AnimeName(title=model.title, anime=model)
                name.save()
                #Not watched and main need to be reloaded
                updateMainCaches(USER_STATUS[0][0])
                ret['id'] = model.id
            except Exception, e:
                form.addError("Error %s has occured. Please make sure that the addition was successful." % e)
    return ret

@render_to('anime/add.html')
def add(request):
    form = AnimeForm()
    if request.method == 'POST' and request.user.is_authenticated():
        result = _addAnimeItem(request)
        try:
            return HttpResponseRedirect('/card/%s/' % result['id'])
        except KeyError:
            form = result['form']
    ctx = {'form': form}
    ctx.update(csrf(request))
    return ctx
