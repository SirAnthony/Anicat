
from django.core.cache import cache
from django.db.models.fields import FieldDoesNotExist
from anime.forms import AnimeForm, UserStatusForm, createFormFromModel
from anime.models import AnimeItem, AnimeName, USER_STATUS, EDIT_MODELS
from anime.functions import updateMainCaches
from datetime import datetime

def addAnimeItem(request):
    response = {}
    form = None
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif not request.user.is_authenticated():
        response['text'] = 'You must be logged in.'
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
                    #Not watched and main need to be reloaded
                    updateMainCaches(USER_STATUS[0][0])
                    response['id'] = model.id
                except Exception, e:
                    form.addError("Error %s has occured. Please make sure that the addition was successful." % e)
    response['form'] = form or AnimeForm()
    return response

def edit(request, itemId, modelname='anime', field=None):
    if not modelname:
        modelname = 'anime'
    response = {'model': modelname, 'id': itemId}
    if not request.user.is_authenticated():
        response['text'] = 'You must be logged in.'
    elif modelname != 'status' and (datetime.now() - request.user.date_joined).days < 20:
        response['text'] = 'You cannot doing this now.'
    elif modelname not in EDIT_MODELS:
        response['text'] = 'Bad model name passed.'
    else:
        form = None
        obj = None
        lastfunc = None
        fields = None
        retid = None
        model = EDIT_MODELS[modelname]
        if field:
            try:
                fields = field.split(',')
                map(lambda x: model._meta.get_field(x), fields)
            except FieldDoesNotExist:
                return {'text': 'Bad fields passed.'}
        formobject = createFormFromModel(model, fields)
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
                retid = itemId
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
        elif modelname == 'links':
            try:
                anime = AnimeItem.objects.get(id=itemId)
            except AnimeItem.DoesNotExist:
                response['text'] = 'Bad id passed.'
            else:
                obj, created = model.objects.get_or_create(anime=anime)
        elif modelname == 'name':
            try:
                obj = AnimeItem.objects.get(id=itemId)
            except AnimeItem.DoesNotExist:
                response['text'] = 'Bad id passed.'
        else:
            try:
                obj = model.objects.get(id=itemId)
            except model.DoesNotExist:
                obj = model()
        if request.method != 'POST':
            try:
                form = formobject(instance=obj)
            except Exception, e:
                response['text'] = str(e)
        else:
            form = formobject(request.POST, instance=obj)
            if obj and form.is_valid():
                try:
                    if modelname == 'name':
                        _saveAnimeNames(form, obj)
                    else:
                        for fieldname in form.cleaned_data:
                            #TODO: Fix title update on AnimeItem 
                            if fieldname != obj._meta.pk.name:
                                setattr(obj, fieldname, form.cleaned_data[fieldname])
                            obj.save()
                except Exception, e:
                    response['text'] = str(e)
                    form.addError('Error "%s" has occured.' % e)
                else:
                    response.update({'response': 'edit', 'status': True, 'id': retid or obj.id, 'text': form.cleaned_data})
                    if lastfunc:
                        lastfunc()
            else:
                response['text'] = form.errors
        response['form'] = form
    return response


def _saveAnimeNames(form, obj):
    if not obj or not obj.id:
        raise ValueError('%s not exists.' % type(obj).__name__)
    names = obj.animenames.all()
    cleaned = form.cleaned_data.values()
    newNames = filter(lambda x: x and x not in names, cleaned)
    oldNames = filter(lambda x: x and x not in cleaned, names)
    if not newNames and len(oldNames) == len(names):
        raise Exception('Cannot delete all names. One name must be left.')
    for name in oldNames:
        try:
            newname = newNames.pop()
        except IndexError:
            name.delete()
            if obj.title == name.title:
                newname = obj.animenames.all()[0]
                obj.title = newname.title
                super(AnimeItem, obj).save() #Does not check again
        else:
            if obj.title == name.title:
                obj.title = newname.title
                super(AnimeItem, obj).save() #Does not check again
            name.title = newname.title
            name.save()
    for name in newNames:
        name.save()