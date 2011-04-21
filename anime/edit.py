
from anime.forms import AnimeForm, UserStatusForm, createFormFromModel
from anime.models import AnimeItem, AnimeName, USER_STATUS, EDIT_MODELS
from anime.functions import updateMainCaches
from django.core.cache import cache
from datetime import datetime

def addAnimeItem(request):
    response = {}
    form = None
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already registred.'
    else:
        form = AnimeForm(request.POST, request.FILES)
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
                    response['id'] = model.id
                except Exception, e:
                    form.addError("Error %s has occured. Please make sure that the addition was successful." % e)
    response['form'] = form or AuthenticationForm()
    return response

def edit(request, itemId, modelname='anime', field=None):
    if not modelname:
        modelname = 'anime'
    response = {}
    if not request.user.is_authenticated():
        response['text'] = 'You must be logged in.'
    elif modelname not in EDIT_MODELS:
        response['text'] = 'Bad model name passed.'
    else:
        form = None
        obj = None
        lastfunc = None
        model = EDIT_MODELS[modelname]
        if field:
            try:
                fields = field.split(',')
                models = map(lambda x: x.name, model._meta.fields)
                for f in fields:
                    if f not in models:
                        raise Exception
            except:
                return {'text' : 'Bad fields passed.'}
        formobject = createFormFromModel(model, field)
        if modelname == 'status':
            try:
                anime = AnimeItem.objects.get(id=itemId)
            except AnimeItem.DoesNotExist:
                response['text'] = 'Bad id passed.'
            else:
                try:
                    obj = model.objects.get(user=request.user, anime=anime)
                except model.DoesNotExist:
                    obj = model(user=request.user, anime=anime, status=0)
                oldstatus = obj.status
                try:
                    status = int(request.POST.get('status'))
                    if not -1 < status < len(USER_STATUS):
                        raise ValueError
                except:
                    status = 0
                def st(status, oldstatus, user):
                    def _f():
                        stat = cache.get('mainTable:%s' % user.id)
                        for s in [status, oldstatus]:
                            try:
                                stat[s] = {}
                            except:
                                pass
                        cache.set('mainTable:%s' % user.id, stat)
                        cache.delete('userCss:%s' % user.id)
                        cache.delete('Stat:%s' % user.id)
                    return _f
                lastfunc = st(status, oldstatus, request.user)
        elif modelname == 'link':
            try:
                anime = AnimeItem.objects.get(id=itemId)
            except AnimeItem.DoesNotExist:
                response['text'] = 'Bad id passed.'
            else:
                obj, created = model.objects.get_or_create(anime=anime)
        else:
            try:
                obj = model.objects.get(id=itemId)
            except model.DoesNotExist:
                obj = model()
        if request.method != 'POST':
            form = formobject(instance=obj)
        else:
            form = formobject(request.POST, instance=obj)
            if obj and form.is_valid():
                for fieldname in form.cleaned_data:
                    if fieldname != obj._meta.pk.name:
                        setattr(obj, fieldname, form.cleaned_data[fieldname])
                try:
                    obj.save()
                except Exception, e:
                    response['text'] = str(e)
                else:
                    response.update({'response': 'editok', 'text': form.cleaned_data})
                    if lastfunc:
                        lastfunc()
            else:
                response['text'] = form.errors
        response['form'] = form
    return response
