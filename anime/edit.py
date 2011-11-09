# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.db.models.fields import FieldDoesNotExist
from anime.forms.create import createFormFromModel
from anime.models import (
            AnimeItem, AnimeLink,
            USER_STATUS, EDIT_MODELS)
from anime.functions import updateMainCaches
from datetime import datetime

EDIBLE_LIST = [
    'state',
    'animerequest',
    'feedback'
]


def edit(request, itemId=0, modelname='anime', field=None, ajaxSet=True):
    if not modelname:
        modelname = 'anime'
    response = {'model': modelname, 'id': itemId}
    if not request.user.is_authenticated():
        response['text'] = 'You must be logged in.'
        if modelname == 'state':
            response.update({'response': 'edit', 'returned': request.POST.get('state')})
    elif modelname not in EDIT_MODELS:
        response['text'] = 'Bad model name passed.'
    elif not request.user.is_active and modelname != 'state':
        response['text'] = 'You cannot doing this.'
    elif modelname not in EDIBLE_LIST and (datetime.now() - request.user.date_joined).days < 15:
        response['text'] = 'You cannot doing this now.'
    else:
        form = None
        obj = None
        lastfunc = None
        fields = None
        retid = None
        model = EDIT_MODELS[modelname]
        try:
            itemId = int(itemId)
        except:
            return {'text': 'Bad id passed.'}
        if field:
            try:
                fields = field.split(',')
                map(lambda x: model._meta.get_field(x), fields)
            except FieldDoesNotExist:
                return {'text': 'Bad fields passed.'}
        formobject = createFormFromModel(model, fields)
        if modelname == 'state':
            try:
                anime = AnimeItem.objects.get(id=itemId)
            except AnimeItem.DoesNotExist:
                response['text'] = 'Bad id passed.'
            else:
                try:
                    obj = model.objects.get(user=request.user, anime=anime)
                except model.DoesNotExist:
                    obj = model(user=request.user, anime=anime, state=0)
                oldstatus = obj.state
                try:
                    status = int(request.POST.get('state'))
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
        elif modelname in ['name', 'links', 'image']:
            try:
                obj = AnimeItem.objects.get(id=itemId)
            except AnimeItem.DoesNotExist:
                response['text'] = 'Bad id passed.'
            retid = itemId
        else:
            try:
                obj = model.objects.get(id=itemId)
            except model.DoesNotExist:
                obj = model()
        if request.method != 'POST' or not ajaxSet:
            try:
                response['form'] = formobject(instance=obj)
                if request.method == 'POST':
                    response.update({
                        'status': True,
                        'response': 'edit',
                        'id': retid or obj.id,
                        'field': field,
                        'text': ''
                    })
            except Exception, e:
                response['text'] = str(e)
        else:
            #FIXME: AnimeNameForm throw exceptions here but nobody catch
            form = formobject(request.POST.copy(),
                    files=request.FILES, user=request.user, instance=obj)
            if obj and form.is_valid():
                try:
                    if modelname == 'name':
                        _saveAnimeNames(form, obj)
                    elif modelname == 'links':
                        _saveAnimeLinks(form, obj)
                    else:
                        if modelname == 'anime' and not itemId:
                            if not fields:
                                obj.save()
                            else:
                                raise ValueError('Cannot save new instance without all required fields.')
                        elif modelname == 'image':
                            obj = form.instance
                            retid = obj.id
                        for fieldname in form.cleaned_data.keys():
                            if fieldname != obj._meta.pk.name:
                                setattr(obj, fieldname, form.cleaned_data[fieldname])
                        obj.save()
                        if modelname == 'anime':
                            updateMainCaches(USER_STATUS[0][0])
                    if modelname in ['animerequest', 'image', 'feedback', 'request']:
                        cache.delete('requests')
                    elif modelname == 'bundle':
                        for item in obj.animeitems.values_list('id').all():
                            cache.delete('card:%s' % item[0])
                    elif modelname != 'state':
                        cache.delete('card:%s' % itemId)
                except Exception, e:
                    response['text'] = str(e)
                    form.addError('Error "%s" has occured.' % e)
                    response['form'] = form
                else:
                    response.update({
                        'response': 'edit',
                        'status': True,
                        'id': retid or obj.id,
                        'field': field,
                        'text': form.cleaned_data
                    })
                    if lastfunc:
                        try:
                            lastfunc()
                        except:
                            pass
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
                #Does not check again
                super(AnimeItem, obj).save()
        else:
            if obj.title == name.title:
                obj.title = newname.title
                #Does not check again
                super(AnimeItem, obj).save()
            name.title = newname.title
            name.save()
    for name in newNames:
        name.save()


def _saveAnimeLinks(form, obj):
    if not obj or not obj.id:
        raise ValueError('%s not exists.' % type(obj).__name__)
    links = list(obj.links.all())
    cleaned = form.cleaned_data
    cleanlinks = [0] * (len(form.cleaned_data) / 2)
    cleantypes = [0] * (len(form.cleaned_data) / 2)
    oldLinks = []
    for name, value in cleaned.items():
        s = name.rsplit(None, 1)[-1]
        if name.find('type') >= 0:
            cleantypes[int(s)] = int(value)
        else:
            cleanlinks[int(s)] = value
    for link in links[:]:
        if link.link in cleanlinks:
            i = cleanlinks.index(link.link)
            if cleantypes[i] and link.linkType != cleantypes[i]:
                link.linkType = cleantypes[i]
            else:
                links.remove(link)
            cleanlinks.pop(i)
            cleantypes.pop(i)
        else:
            oldLinks.append(links.pop(links.index(link)))
    # Now in links only modified links,
    # in cleanlinks - links that must be added to db,
    # in oldlinks - links that must be removed
    for link in cleanlinks[:]:
        i = cleanlinks.index(link)
        if not link:
            cleanlinks.pop(i)
            cleantypes.pop(i)
            continue
        if len(oldLinks):
            l = oldLinks.pop()
            l.link = cleanlinks.pop(i)
            l.linkType = cleantypes.pop(i)
            links.append(l)
        else:
            links.append(AnimeLink(anime=obj, link=cleanlinks.pop(i), linkType=cleantypes.pop(i)))
    for link in oldLinks:
        link.delete()
    for l in links:
        l.save()
