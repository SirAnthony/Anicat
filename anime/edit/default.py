
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.db.models.fields import FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _

from anime.core import FieldExplorer, GetError
from anime.forms.create import createFormFromModel
from anime.models import AnimeItem, EDIT_MODELS


class EditError(Exception):
    def __init__(self, message, code=None, params=None):
        import operator
        from django.utils.encoding import force_unicode
        if isinstance(message, dict):
            self.message_dict = message
            # Reduce each list of messages into a single list.
            message = reduce(operator.add, message.values())
        if isinstance(message, list):
            self.messages = [force_unicode(msg) for msg in message]
        else:
            self.code = code
            self.params = params
            self.messages = force_unicode(message)

    def __str__(self):
        if hasattr(self, 'message_dict'):
            return repr(self.message_dict)
        if isinstance(self.messages, basestring):
            return str(self.messages)
        return repr(self.messages)

    def __repr__(self):
        if hasattr(self, 'message_dict'):
            return 'EditError({0})'.format(repr(self.message_dict))
        return 'EditError({0})'.format(repr(self.messages))



EDITABLE_LIST = [
    'state',
    'request',
    'animerequest',
    'feedback'
]


class EditableDefault(object):
    error_messages = {
        'not_loggined': _('You must be logged in.'),
        'bad_model': _('Bad model name passed.'),
        'bad_id': _('Bad id passed.'),
        'bad_fields': _('Bad fields passed.'),
        'bad_request': _('Bad request type.'),
        'bad_form': _('Bad form.'),
        'forbidden': _('You cannot do this.'),
        'wait': _('You cannot do this now. Please wait for {0} days.'),
        'error': _('Error "{0}" has occured.'),
    }

    def __init__(self, request, item_id=0, modelname='anime', field=None):
        if hasattr(self, 'extra_error_messages'):
            self.error_messages.update(self.extra_error_messages)
        if not request.user.is_authenticated():
            raise EditError(self.error_messages['not_loggined'])
        elif modelname not in EDIT_MODELS:
            raise EditError(self.error_messages['bad_model'])
        elif not request.user.is_active and modelname not in EDITABLE_LIST:
            raise EditError(self.error_messages['forbidden'])
        elif (datetime.now() - request.user.date_joined).days < 15:
            raise EditError(self.error_messages['wait'].format(
                settings.DAYS_BEFORE_EDIT - (
                    datetime.now() - request.user.date_joined).days))

        try:
            self.item_id = int(item_id)
        except:
            raise EditError(self.error_messages['bad_id'])

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
                raise EditError(self.error_messages['bad_fields'])

        self.setObject()

    def setObject(self):
        try:
            self.obj = self.model.objects.get(id=self.item_id)
        except self.model.DoesNotExist:
            self.obj = self.model()

    def process(self, rtype):
        formobject = createFormFromModel(self.model, self.fields)
        #if not formobject:
        #    raise EditError(self.error_messages['bad_form'])
        try:
            f = getattr(self, rtype.lower())
        except AttributeError:
            raise EditError(self.error_messages['bad_request'])
        r = f(formobject)
        if f == self.post:
            try:
                #TODO: rename to post_save()?
                self.last()
            except Exception:
                pass
        return r

    def get(self, formobject, data=None):
        r = {'form': formobject(data, instance=self.obj)}
        return r

    def form(self, formobject, data=None):
        r = self.get(formobject, data)
        r.update({
            'status': True,
            'id': self.retid or getattr(self.obj, 'id', 0) or 0,
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
                raise EditError('')
            self.save(form, self.obj)
        except Exception, e:
            #if not isinstance(e, EditError):
            #    pass
            if unicode(e):
                form.addError(self.error_messages['error'].format(e))
            ret['text'] = form.errors
            ret['form'] = form
        else:
            ret['response'] = 'edit'
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
        retid = self.retid or getattr(self.obj, 'id', 0)
        anime = AnimeItem.objects.get(id=retid)
        return self.explore_result_item(anime)

    def explore_result_item(self, anime):
        ret = {}
        field_expl = FieldExplorer(self.field or self.modelname)
        try:
            ret['text'] = field_expl.get_value(anime, self.request)
        except GetError, e:
            ret['text'] = e.message
            ret['status'] = False
        return ret

    def last(self):
        cache.delete('card:%s' % self.item_id)


