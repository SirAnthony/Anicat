
from datetime import datetime
from django.core.cache import cache
from django.db.models.fields import FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _

from anime.core import FieldExplorer, GetError
from anime.forms.create import createFormFromModel
from anime.models import AnimeItem, EDIT_MODELS


class EditError(Exception):
    pass


EDITABLE_LIST = [
    'state',
    'request',
    'animerequest',
    'feedback'
]


class EditableDefault(object):

    def __init__(self, request, item_id=0, modelname='anime', field=None):
        if not request.user.is_authenticated():
            raise EditError(_('You must be logged in.'))
        elif modelname not in EDIT_MODELS:
            raise EditError(_('Bad model name passed.'))
        elif not request.user.is_active and modelname not in EDITABLE_LIST:
            raise EditError(_('You cannot do this.'))
        elif (datetime.now() - request.user.date_joined).days < 15:
            raise EditError(_('You cannot do this now. Please wait for {0} days.'.format(
                15 - (datetime.now() - request.user.date_joined).days)))

        try:
            self.item_id = int(item_id)
        except:
            raise EditError(_('Bad id passed.'))

        self.request = request
        self.model = EDIT_MODELS[modelname]
        self.modelname = modelname
        self.field = field
        self.retid = self.item_id
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
            self.obj = self.model.objects.get(id=self.item_id)
        except self.model.DoesNotExist:
            self.obj = self.model()

    def process(self, rtype):
        formobject = createFormFromModel(self.model, self.fields)
        try:
            f = getattr(self, rtype)
        except AttributeError:
            raise EditError(_('Bad request type.'))
        r = f(formobject)
        if f == self.post:
            try:
                #TODO: rename to post_save()?
                self.last()
            except Exception:
                pass
        return r

    def get(self, formobject, data=None):
        if not formobject:
            return {}
        r = {'form': formobject(data, instance=self.obj)}
        # FIXME: cruve
        if self.request.method == 'POST':
            r.update({
                'status': True,
                'id': self.retid or getattr(self.obj, 'id', 0),
                'text': None
            })
        return r

    def post(self, formobject):
        self.form = form = formobject(self.request.POST.copy(),
                files=self.request.FILES, user=self.request.user,
                instance=self.obj)
        ret = {}
        try:
            if not self.obj or not form.is_valid():
                raise EditError
            self.save(form, self.obj)
        except Exception, e:
            #if not isinstance(e, EditError):
            #    pass
            if unicode(e):
                form.addError('Error "%s" has occured.' % unicode(e))
            ret['text'] = form.errors
            ret['form'] = form
        else:
            ret['status'] = True
            ret.update(self.explore_result())
        ret['id'] = self.retid or getattr(self.obj, 'id', 0) or 0
        return ret

    def save(self, form, obj):
        for fieldname in form.cleaned_data.keys():
            if fieldname != obj._meta.pk.name:
                setattr(obj, fieldname, form.cleaned_data[fieldname])
        obj.save()

    def explore_result(self):
        ret = {}
        retid = self.retid or getattr(self.obj, 'id', 0)
        anime = AnimeItem.objects.get(id=retid)
        field_expl = FieldExplorer(self.field or self.modelname)
        try:
            ret['text'] = field_expl.get_value(anime, self.request)
        except GetError, e:
            ret['text'] = e.message
            ret['status'] = False
        return ret

    def last(self):
        cache.delete('card:%s' % self.item_id)


