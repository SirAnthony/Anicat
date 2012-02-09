
from collections import defaultdict
from django.core.exceptions import ValidationError
from django.forms import ChoiceField, CharField, HiddenInput, widgets
from django.utils.translation import ugettext_lazy as _
from anime.forms.ModelError import ErrorModelForm
from anime.forms.fields import TextToAnimeItemField, TextToAnimeNameField, TextToAnimeLinkField
from anime.models import AnimeItem, AnimeBundle, LINKS_TYPES


class DynamicModelForm(ErrorModelForm):
    error_messages = {
        'noinstance': _('Instance not passed.'),
        'notexist':  _('Record not exist.'),
        'badinstance': _('{0} is not {1} instance.'),
    }


    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        instance_type = kwargs.pop('instance_type', AnimeItem)
        instance_saved = kwargs.pop('instance_saved', True)
        if not instance:
            raise ValueError(unicode(self.error_messages['noinstance']))
        if instance_saved and not instance.id:
            raise ValueError(unicode(self.error_messages['notexist']))
        if not isinstance(instance, instance_type):
            raise TypeError(self.error_messages['badinstance'].format(
                type(instance).__name__, instance_type.__name__))
        #Fixme: I did not recognize why self.instance blanked in clean method.
        self._instance = instance
        super(DynamicModelForm, self).__init__(*args, **kwargs)

    def getDataCount(self, data, name, relatedname, default=1):
        items = []
        count = default
        if data:
            count = max([int(x.split()[-1]) \
                for x in data.keys() if x.startswith(name)] \
                or [default,]) + 1
        else:
            if self._instance.id:
                try:
                    items = getattr(self._instance, relatedname).all()
                except (AttributeError, TypeError):
                    pass
                count = len(items) + default
        return count, items

    def setFields(self, kwds):
        def compare(x, y):
            try:
                x = int(x.rsplit(None, 1)[1])
            except:
                x = -1
            try:
                y = int(y.rsplit(None, 1)[1])
            except:
                y = -1
            return cmp(x, y)

        keys = kwds.keys()
        keys.sort(cmp=compare)
        for k in keys:
            self.fields[k] = kwds[k]

    def setData(self, kwds):
        if not kwds:
            return
        keys = kwds.keys()
        keys.sort()
        for name, field in self.fields.items():
            self.data[name] = field.widget.value_from_datadict(kwds, self.files, self.add_prefix(name))
        self.is_bound = True


class AnimeBundleForm(DynamicModelForm):
    extra_error_messages = {
        'one_item': _('It must be at least two items to tie.'),
        'no_item': _('You cannot create new bundle for item without include it.'),
        'equal_item': _('You cannot tie item to itself.'),
        'not_unique': _('This item is not unique.'),
    }
    _currentid = None

    def __init__(self, data=None, *args, **kwargs):
        try:
            if data and 'currentid' in data:
                self._currentid = int(data.get('currentid'))
                if len([x for x in data.keys() if x.startswith('Bundle ')]) < 1:
                    data = None
        except:
            pass
        super(AnimeBundleForm, self).__init__(data, *args,
              instance_type=AnimeBundle, instance_saved=False, **kwargs)
        self.error_messages.update(self.extra_error_messages)
        instance = self._instance
        fields = {}
        (fieldsCount, items) = self.getDataCount(data, 'Bundle ', 'animeitems', 2)
        for i in range(fieldsCount):
            try:
                initial = items[i].title
            except:
                initial = None
                if i == 0 and self._currentid:
                    try:
                        initial = AnimeItem.objects.get(id=self._currentid).title
                    except:
                        pass
            field = TextToAnimeItemField(initial=initial, required=False)
            fields['Bundle %i' % i] = field
        if self._currentid:
            fields['currentid'] = CharField(initial=self._currentid,
                show_hidden_initial=True, widget=HiddenInput(attrs={
                    "id": "currentid_b_{0}".format(instance.id or 0)}),
                required=False)
        self.setFields(fields)
        self.setData(data)

    def clean(self):
        if 'currentid' in self.cleaned_data:
            del self.cleaned_data['currentid']
        self._validate_unique = True
        if not self._instance.id:
            iv = [x for x in self.cleaned_data.itervalues() if x]
            if len(iv) == 1:
                raise ValidationError(self.error_messages['one_item'])
            elif len(iv) > 1:
                if self._currentid and \
                   not len([x for x in iv if x.id == self._currentid]):
                    raise ValidationError(self.error_messages['no_item'])
        l = {}
        for k, v in self.cleaned_data.items():
            if not v:
                continue
            if v in l:
                if l[v] in self.cleaned_data:
                    self._errors[l[v]] = self.error_class([self.error_messages['not_unique']])
                self._errors[k] = self.error_class([self.error_messages['equal_item']])
            else:
                l[v] = k
        return self.cleaned_data

#TODO: inherit from YobaDynamicModelForm


class AnimeNameForm(DynamicModelForm):
    def __init__(self, data=None, *args, **kwargs):
        super(AnimeNameForm, self).__init__(data, *args, **kwargs)
        instance = self._instance
        fields = {}
        (count, items) = self.getDataCount(data, 'Name ', 'animenames', default=4)
        for i in range(count):
            try:
                initial = items[i].title.strip()
            except:
                initial = None
            field = TextToAnimeNameField(initial=initial, required=False)
            field._animeobject = instance
            fields['Name %i' % i] = field
        for fieldname in self.fields.keys():
            del self.fields[fieldname]
        self.setFields(fields)
        self.setData(data)


class AnimeLinksForm(DynamicModelForm):

    class Meta:
        exclude = ('anime')

    def __init__(self, data=None, *args, **kwargs):
        super(AnimeLinksForm, self).__init__(data, *args, **kwargs)
        instance = self._instance
        fields = {}
        (count, items) = self.getDataCount(data, 'Link type ', 'links', default=3)
        for i in range(count):
            try:
                link = items[i].link.strip()
                ltype = items[i].linkType
            except:
                link = None
                ltype = 0
            field_link = TextToAnimeLinkField(initial=link, required=False)
            field_type = ChoiceField(choices=LINKS_TYPES, initial=ltype,
                            widget=widgets.Select(attrs={'class': 'linktype'}))
            field_type._linkfield = field_link
            fields['Link {0}'.format(i)] = field_link
            fields['Link type {0}'.format(i)] = field_type
        for fieldname in self.fields.keys():
            del self.fields[fieldname]
        self.setFields(fields)
        self.setData(data)

    def _clean_fields(self):
        super(AnimeLinksForm, self)._clean_form()
        for tp in [ChoiceField, TextToAnimeLinkField]:
            for name, field in filter(lambda x: isinstance(x[1], tp), self.fields.items()):
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
                try:
                    value = field.clean(value)
                    self.cleaned_data[name] = value
                    if hasattr(self, 'clean_%s' % name):
                        value = getattr(self, 'clean_%s' % name)(self)
                        self.cleaned_data[name] = value
                except ValidationError, e:
                    self._errors[name] = self.error_class(e.messages)
                    if name in self.cleaned_data:
                        del self.cleaned_data[name]
                else:
                    if tp is ChoiceField:
                        field._linkfield._linktype = int(value)
        for name, field in filter(lambda x: isinstance(x[1], ChoiceField), self.fields.items()):
            if not self._errors.has_key(name):
                self.data[name] = field._linkfield._linktype
                self.cleaned_data[name] = str(field._linkfield._linktype)

