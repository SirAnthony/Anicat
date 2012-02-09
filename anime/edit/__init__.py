# -*- coding: utf-8 -*-

from anime.edit.default import EditError, EditableDefault
from anime.edit.simple import Anime, State, Bundle
from anime.edit.animebased import Name, Links
from anime.edit.requests import (Request, Animerequest, Feedback, Image)


def edit(request, item_id=0, modelname='anime', field=None, form=False):
    if not modelname:
        modelname = 'anime'
    response = {
        'response': 'form',
        'status': False,
        'id': item_id,
        'model': modelname,
        'field': field
    }

    try:
        editable = globals()[modelname.capitalize()]
    except KeyError:
        editable = EditableDefault
    try:
        eobj = editable(request, item_id, modelname, field)
        response.update(
            eobj.process('form' if form else request.method))
    except EditError, e:
        response['text'] = unicode(e)
    except Exception, e:
        return {'text': unicode(e)}
    return response


