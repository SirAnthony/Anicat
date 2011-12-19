
from django.core.exceptions import ValidationError
from django.forms import ChoiceField
from django.utils.translation import ugettext_lazy as _
from anime.forms.ModelError import ErrorModelForm
from anime.forms.fields import TextToAnimeItemField, TextToAnimeNameField, TextToAnimeLinkField
from anime.models import AnimeBundle, AnimeItem, LINKS_TYPES


class DynamicModelForm(ErrorModelForm):

    def setFields(self, kwds):
        keys = kwds.keys()
        keys.sort(cmp=lambda x, y: cmp(int(x.rsplit(None, 1)[1]), int(y.rsplit(None, 1)[1])))
        for k in keys:
            self.fields[k] = kwds[k]

    def setData(self, kwds):
        if not kwds:
            return
        keys = kwds.keys()
        keys.sort()
        for name,field in self.fields.items():
            self.data[name] = field.widget.value_from_datadict(kwds, self.files, self.add_prefix(name))
        self.is_bound = True


class AnimeBundleForm(DynamicModelForm):

    def __init__(self, data=None, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(AnimeBundleForm, self).__init__(data, *args, **kwargs)
        if instance:
            if not isinstance(instance, AnimeBundle):
                raise TypeError('%s is not AnimeBundle instance.' % type(instance).__name__)
            items = ()
            fields = {}
            if instance.id:
                if data:
                    fieldsCount = max([int(x.split()[-1]) for x in data.keys() if x.startswith('Bundle ')])
                else:
                    items = instance.animeitems.all()
                    fieldsCount = len(items)
            else:
                fieldsCount = 1
            for i in range(fieldsCount + 1):
                try:
                    initial = items[i].title
                except:
                    initial = None
                field = TextToAnimeItemField(initial=initial, required=False)
                fields['Bundle %i' % i] = field
            self.setFields(fields)
            self.setData(data)

    def clean(self):
        self._validate_unique = True
        if len(filter(None, self.cleaned_data.itervalues())) < 2:
            raise ValidationError(_('It must be at least two items to tie.'))
        return self.cleaned_data

#TODO: inherit from YobaDynamicModelForm


class AnimeNameForm(DynamicModelForm):
    def __init__(self, data=None, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if not instance or not instance.id:
            raise ValueError(_('Record not exist.'))
        if not isinstance(instance, AnimeItem):
            raise TypeError('%s is not AnimeItem instance.' % type(instance).__name__)
        super(AnimeNameForm, self).__init__(data, *args, **kwargs)
        fields = {}
        if data:
            count = max([int(x.split()[-1]) for x in data.keys() if x.startswith('Name ')]) + 1
        else:
            items = instance.animenames.all()
            count = len(items) + 4
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
        instance = kwargs.pop('instance', None)
        if not instance or not instance.id:
            raise ValueError(_('Record not exist.'))
        if not isinstance(instance, AnimeItem):
            raise TypeError('%s is not AnimeItem instance.' % type(instance).__name__)
        super(AnimeLinksForm, self).__init__(data, *args, **kwargs)
        fields = {}
        if data:
            count = max([int(x.split()[-1]) for x in data.keys() if x.startswith('Link type ')]) + 1
        else:
            items = instance.links.all()
            count = len(items) + 3
        for i in range(count):
            try:
                link = items[i].link.strip()
                ltype = items[i].linkType
            except:
                link = None
                ltype = 0
            field_link = TextToAnimeLinkField(initial=link, required=False)
            field_type = ChoiceField(choices=LINKS_TYPES, initial=ltype)
            field_type._linkfield = field_link
            fields['Link %i' % i] = field_link
            fields['Link type %i' % i] = field_type
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
                        value = getattr(self, 'clean_%s' % name)()
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

