from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.forms import Form, ModelForm, TextInput, FileField, DateField, BooleanField, CharField
from django.forms.forms import BoundField
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from anime.models import AnimeBundle, AnimeItem, AnimeName, UserStatusBundle, AnimeLinks, DATE_FORMATS
import datetime
import time

#dirty but works
INPUT_FORMATS = (
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
    '%b %d %Y', '%b %d, %Y',
    '%d %b %Y', '%d %b, %Y',
    '%B %d %Y', '%B %d, %Y',
    '%d %B %Y', '%d %B, %Y',
)

class ErrorForm(Form):
    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

class ErrorModelForm(ModelForm):
    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

    def as_json(self):
        #TODO: no checkboxes, radiobuttons or textareas
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []

        for name, field in self.fields.items():
            html_class_attr = None
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors])
            fieldobj = {
                'id': bf.auto_id,
                'name': bf.name,
                'value': bf.value(),
                'tag': 'input',
            }
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                fieldobj['type'] = 'hidden'
            else:
                if hasattr(field.widget, 'choises'):
                    fieldobj['tag'] = 'select'
                    fieldobj['type'] = 'select'
                    sel = {}
                    for c in field.widget.choises:
                        sel[c.pk] = force_unicode(c)
                    fieldobj['select'] = sel
                else:
                    try:
                        fieldobj['type'] = field.widget.input_type
                    except AttributeError:
                        pass
                try:
                    html_class_attr = bf.css_classes().split()
                except:
                    pass

                if field.help_text:
                    help_text = force_unicode(field.help_text)
                else:
                    help_text = None

                output.append({
                    'errors': bf_errors,
                    'field': fieldobj,
                    'help_text': help_text,
                    'html_class_attr': html_class_attr
                })

        if top_errors:
            output.extend(0, top_errors)
        if hidden_fields: # Insert any hidden fields in the last row.
            for field in hidden_fields:
                output.append(field)
        return output

    class Meta:
        pass

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

class TextToAnimeItemField(CharField):
    def to_python(self, value):
        if not value:
            return None
        try:
            ivalue = int(value)
            value = AnimeItem.objects.get(id=ivalue)
        except:
            try:
                value = AnimeItem.objects.get(title=value)
            except AnimeItem.DoesNotExist, e:
                raise ValidationError(e)
            except AnimeItem.MultipleObjectsReturned, e:
                raise ValidationError('Too many items with such title, try to use id instead title.')
        return value

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
                items = instance.animeitems.all()
                fieldsCount = len(items) + 1
            else:
                fieldsCount = 2
            for i in range(fieldsCount):
                try:
                    initial = items[i].title
                except:
                    initial = None
                field = TextToAnimeItemField(initial=initial, required=False)
                fields['bundle %i' % i] = field
            self.setFields(fields)
            self.setData(data)


class CalendarWidget(TextInput):
    class Media:
        js = ("calendar.js", "DateTimeShortcuts.js")

    def __init__(self, attrs={}):
        self._known = 0
        super(CalendarWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'})

    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.date):
            try:
                value = value.strftime(DATE_FORMATS[self._known])
            except:
                value = 'Bad value'
        return super(CalendarWidget, self).render(name, value, attrs)


class UnknownDateField(DateField):
    widget=CalendarWidget
    cleaned_data = {}

    def __init__(self, *args, **kwargs):
        super(UnknownDateField, self).__init__(*args, **kwargs)
        self.input_formats = DATE_FORMATS + INPUT_FORMATS

    #Not needed if changeset > 16137
    def to_python(self, value):
        """
        Validates that the input can be converted to a date. Returns a Python
        datetime.date object.
        """
        if value in EMPTY_VALUES:
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        for format in self.input_formats:
            try:
                return self.strptime(value, format)
            except ValueError:
                continue
        raise ValidationError(self.error_messages['invalid'])

    def strptime(self, value, format):
        date = datetime.date(*time.strptime(value, format)[:3])
        #cs > 16137
        #date = super(UnknownDateField, self).strptime(self, value, format)
        label = self.label.lower()
        try:
            self.cleaned_data[label + 'Known'] = DATE_FORMATS.index(format)
            for field in ('released', 'ended'):
                if field == label:
                    self.cleaned_data[u'air'] = True if date >= date.today() else False
        except ValueError:
            self.cleaned_data[label + 'Known'] = 0
        return date

class AnimeForm(ErrorModelForm):
    releasedAt = UnknownDateField(label='Released')
    endedAt = UnknownDateField(label='Ended', required=False)
    
    def __init__(self, *args, **kwargs):
        super(AnimeForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            for field in ['released', 'ended']:
                try:
                    self.fields[field + 'At'].widget._known = getattr(self.instance, field + 'Known')
                except:
                    continue

    def _clean_form(self):
        super(AnimeForm, self)._clean_form()
        for name, field in self.fields.items():
            try:
                self.cleaned_data.update(getattr(field, 'cleaned_data'))
            except AttributeError:
                pass

    class Meta():
        model = AnimeItem
        exclude = ('bundle', 'locked', 'releasedKnown', 'endedKnown')

class TextToAnimeNameField(CharField):
    def to_python(self, value):
        try:
            value = value.strip()
            if not value:
                raise ValueError
        except:
            return None
        if not self._animeobject:
            raise ValidationError('AnimeItem not set.')
        try:
            value, create = AnimeName.objects.get_or_create(anime=self._animeobject, title=value)
        except:
            raise ValidationError(e)
        return value

class AnimeNameForm(DynamicModelForm):
    def __init__(self, data=None, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if not instance or not instance.id:
            raise ValueError('Record not exist.')
        if not isinstance(instance, AnimeItem):
            raise TypeError('%s is not AnimeName instance.' % type(instance).__name__)
        super(AnimeNameForm, self).__init__(data, *args, **kwargs)
        fields = {}
        items = instance.animenames.all()
        for i in range(len(items) + 4):
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

class UserStatusForm(ModelForm):
    class Meta:
        model = UserStatusBundle
        exclude = ('anime', 'user')

class UploadMalListForm(ErrorForm):
    file = FileField(max_length=200)
    rewrite = BooleanField(label='Overwrite existing data', required=False)

class UserCreationFormMail(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationFormMail, self).__init__(*args, prefix='register', **kwargs)
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('username', 'email')

class LinksForm(ErrorModelForm):
    class Meta:
        exclude = ('anime')

EDIT_FORMS = {
    AnimeBundle: AnimeBundleForm,
    AnimeItem: AnimeForm,
    AnimeName: AnimeNameForm,
    UserStatusBundle: UserStatusForm,
    AnimeLinks: LinksForm,
}

def createFormFromModel(model, fields=None):
    parent = ErrorModelForm
    if model in EDIT_FORMS:
        parent = EDIT_FORMS[model]
    m = model
    f = fields
    #raise Exception
    class _ModelForm(parent):
        __fields = f
        def __init__(self, *args, **kwargs):
            super(_ModelForm, self).__init__(*args, **kwargs)
            if self.__fields:
                for fieldname in self.fields.keys():
                    if fieldname not in self.__fields:
                        del self.fields[fieldname]

        class Meta(parent.Meta):
            model = m
            fields = f
    return _ModelForm