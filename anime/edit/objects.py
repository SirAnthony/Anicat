
from datetime import datetime
from django.core.cache import cache
from django.db.models.fields import FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _

from anime.core import FieldExplorer
from anime.forms.create import createFormFromModel
from anime.functions import updateMainCaches
from anime.models import (AnimeItem, USER_STATUS, EDIT_MODELS)



class EditError(Exception):
    pass


EDITABLE_LIST = [
    'state',
    'animerequest',
    'feedback'
]


class EditableDefault(object):

    def __init__(self, request, itemId=0, modelname='anime', field=None):
        if not request.user.is_authenticated():
            raise EditError(_('You must be logged in.'))
        elif modelname not in EDIT_MODELS:
            raise EditError(_('Bad model name passed.'))
        elif not request.user.is_active and modelname != 'state':
            raise EditError(_('You cannot do this.'))
        elif modelname not in EDITABLE_LIST and (
                datetime.now() - request.user.date_joined).days < 15:
            raise EditError(_('You cannot do this now. Please wait for {0} days.'.format(
                15 - (datetime.now() - request.user.date_joined).days)))
        try:
            self.itemId = int(itemId)
        except:
            raise EditError(_('Bad id passed.'))

        self.request = request
        self.model = EDIT_MODELS[modelname]
        self.modelname = modelname
        self.field = field
        self.retid = None
        self.fields = None

        if field:
            try:
                self.fields = field.split(',')
                map(lambda x: self.model._meta.get_field(x), self.fields)
            except FieldDoesNotExist:
                raise EditError(_('Bad fields passed.'))

        self.setObject()

    def setObject(self):
        try:
            self.obj = self.model.objects.get(id=self.itemId)
        except self.model.DoesNotExist:
            self.obj = self.model()

    def process(self, rtype):
        formobject = createFormFromModel(self.model, self.fields)
        try:
            f = getattr(self, rtype)
        except AttributeError:
            raise EditError(_('Bad request type.'))
        r = f(formobject)
        try:
            self.last()
        except AttributeError:
            pass
        return r

    def get(self, formobject):
        if not formobject:
            return {}
        r = {'form': formobject(instance=self.obj)}
        # FIXME: cruve
        if self.request.method == 'POST':
            r.update({
                'status': True,
                'id': self.retid or getattr(self.obj, 'id', 0),
                'text': None
            })
        return r

    def post(self, formobject):
        form = formobject(self.request.POST.copy(),
                files=self.request.FILES, user=self.request.user,
                instance=self.obj)
        ret = {}
        try:
            if not self.obj or not form.is_valid():
                raise EditError
            self.save(form, self.obj)
        except Exception, e:
            if not isinstance(e, EditError):
                raise
            if unicode(e):
                form.addError('Error "%s" has occured.' % unicode(e))
            ret['text'] = form.errors
            ret['form'] = form
        else:
            ret['status'] = True
            field_expl = FieldExplorer(self.field or self.modelname)
            retid = self.retid or getattr(self.obj, 'id', 0)
            if self.modelname == 'bundle': #FUU
                try:
                    anime = AnimeItem.objects.filter(bundle = retid)[0]
                    ret['currentid'] = anime.id
                except IndexError:
                    anime = None
            else:
                anime = AnimeItem.objects.get(id = retid)
            ret['text'] = field_expl.get_value(anime, self.request)

        ret['id'] = self.retid or getattr(self.obj, 'id', 0)
        return ret

    def save(self, form, obj):
        for fieldname in form.cleaned_data.keys():
            if fieldname != obj._meta.pk.name:
                setattr(obj, fieldname, form.cleaned_data[fieldname])
        obj.save()

    def last(self):
        cache.delete('card:%s' % self.itemId)


class Anime(EditableDefault):

    def save(self, form, obj):
        if not self.itemId:
            if not self.fields:
                obj.save()
            else:
                raise ValueError(_('Cannot save new instance without all required fields.'))
        super(Anime, self).save(form, obj)

    def last(self):
        updateMainCaches(USER_STATUS[0][0])
        cache.delete('card:%s' % self.itemId)


class State(EditableDefault):

    def setObject(self):
        try:
            anime = AnimeItem.objects.get(id=self.itemId)
        except AnimeItem.DoesNotExist:
            raise EditError(_('Bad id passed.'))
        try:
            obj = self.model.objects.get(user=self.request.user, anime=anime)
        except self.model.DoesNotExist:
            obj = self.model(user=self.request.user, anime=anime, state=0)
        self.oldstatus = obj.state
        self.obj = obj
        try:
            self.status = int(self.request.POST.get('state'))
            if not -1 < self.status < len(USER_STATUS):
                raise EditError(_('Status value not valid.'))
        except:
            self.status = 0
        self.retid = self.itemId

    def last(self):
        user = self.request.user
        stat = cache.get('mainTable:%s' % user.id)
        for s in [self.status, self.oldstatus]:
            try:
                stat[s] = {}
            except:
                pass
        cache.set('mainTable:%s' % user.id, stat)
        cache.delete('userCss:%s' % user.id)
        cache.delete('Stat:%s' % user.id)


class Bundle(EditableDefault):

    def last(self):
        for item in self.obj.animeitems.values_list('id').all():
            cache.delete('card:%s' % item[0])
