# -*- coding: utf-8 -*-

from anime.edit.objects import (EditError, EditableDefault,
                                Anime, State, Bundle)
from anime.edit.animebased import Name, Links
from anime.edit.requests import (Request, Animerequest, Feedback, Image)


def edit(request, itemId=0, modelname='anime', field=None, ajaxSet=True):
    if not modelname:
        modelname = 'anime'
    response = {
        'response': 'edit',
        'status': False,
        'id': itemId,
        'model': modelname,
        'field': field
    }

    try:
        editable = globals()[modelname.capitalize()]
    except KeyError:
        editable = EditableDefault
    try:
        eobj = editable(request, itemId, modelname, field)
        response.update(
            eobj.process('get' if not ajaxSet else request.method.lower()))
    except EditError, e:
        response['text'] = unicode(e)
    except Exception, e:
        return {'text': unicode(e)}
    return response


