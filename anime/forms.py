from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.forms import Form, ModelForm, TextInput, Textarea, FileField, ImageField, DateField, \
                         BooleanField, CharField
from django.forms.forms import BoundField
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from anime.models import AnimeBundle, AnimeItem, AnimeName, UserStatusBundle, AnimeLinks, AnimeRequest, \
                         AnimeItemRequest, AnimeImageRequest, AnimeFeedbackRequest, DATE_FORMATS
import datetime
import time
import os

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
            dindex = DATE_FORMATS.index(format)
            self.cleaned_data[label + 'Known'] = dindex
            if label == 'ended':
                date = self.get_last_date(date, dindex)
            for field in ('released', 'ended'):
                if field == label:
                    self.cleaned_data[u'air'] = True if date >= date.today() else False
        except ValueError:
            self.cleaned_data[label + 'Known'] = 0
        return date

    def get_last_date(self, date, format_index):
        if format_index & 4: # year
            date = date.replace(year=date.max.year)
        if format_index & 2: # month
            date = date.replace(month=date.max.month)
        if format_index & 1: #day
            date = date.replace(day=1, month=(date.month%12)+1) - datetime.timedelta(1)
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
            raise TypeError('%s is not AnimeItem instance.' % type(instance).__name__)
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

class UserStatusForm(ErrorModelForm):
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

class RequestForm(ErrorModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        instance = kwargs.get('instance', None)
        super(RequestForm, self).__init__(*args, **kwargs)
        if instance and user:
            instance.user = user

    class Meta:
        exclude = ('user', 'anime', 'status')

class AnimeItemRequestForm(RequestForm):
    text = CharField(label="Request anime", widget=Textarea)
    class Meta:
        exclude = ('user', 'anime', 'requestType', 'reason', 'status')

class CardImageField(ImageField):

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid image (GIF, JPG,
        PNG). Resize image if it is biggest than allowed.
        """
        f = super(ImageField, self).to_python(data)
        if f is None:
            return None
        # Try to import PIL in either of the two ways it can end up installed.
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        try:
            from PIL import Image
        except ImportError:
            import Image
        # We need to get a file object for PIL. We might have a path or we might
        # have to read the data into memory.
        if hasattr(data, 'temporary_file_path'):
            file = data.temporary_file_path()
        else:
            if hasattr(data, 'read'):
                file = StringIO(data.read())
            else:
                file = StringIO(data['content'])
        try:
            # load() is the only method that can spot a truncated JPEG,
            #  but it cannot be called sanely after verify()
            trial_image = Image.open(file)
            trial_image.load()
            if trial_image.format not in ('PNG', 'JPEG', 'GIF'):
                raise ValueError('Only PNG, JPEG and GIF formats are accepted.')
            if max(trial_image.size) >= 800:
                raise ValueError('Image too big.')
            # Since we're about to use the file again we have to reset the
            # file object if possible.
            if hasattr(file, 'reset'):
                file.reset()
            # verify() is the only method that can spot a corrupt PNG,
            #  but it must be called immediately after the constructor
            trial_image = Image.open(file)
            trial_image.verify()
        except ImportError:
            # Under PyPy, it is possible to import PIL. However, the underlying
            # _imaging C module isn't available, so an ImportError will be
            # raised. Catch and re-raise.
            raise
        except Exception, e: # Python Imaging Library doesn't recognize it as an image
            raise ValidationError(self.error_messages['invalid_image'] + ' ' + str(e))
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f

class ImageRequestForm(RequestForm):
    text = CardImageField(max_length=150, label='File')
    def __init__(self, *args, **kwargs):
        anime = kwargs.pop('instance', None)
        if not anime or not anime.id:
            raise ValueError('Record not exist.')
        if not isinstance(anime, AnimeItem):
            raise TypeError('%s is not AnimeItem instance.' % type(anime).__name__)
        instance = AnimeImageRequest(anime=anime)
        super(ImageRequestForm, self).__init__(*args, instance=instance, **kwargs)
        self.files = kwargs.get('files', None)

    def _clean_fields(self):
        name = 'text'
        super(ImageRequestForm, self)._clean_fields()
        if name in self.errors:
            return
        image = self.files.get(name)
        try:
            if not image:
                raise ValidationError('This field is required.')
            filename = str(image.size)+image.name
            fullfilename = os.path.join(settings.MEDIA_ROOT, filename)
            if os.path.exists(fullfilename):
                raise ValidationError('This file already loaded.')
            try:
                fileobj = open(fullfilename, 'wb+')
                for chunk in image.chunks():
                    fileobj.write(chunk)
                fileobj.close()
            except Exception, e:
                raise ValidationError(e)
            self.cleaned_data[name] = filename
        except ValidationError, e:
            self._errors[name] = self.error_class(e.messages)
            if name in self.cleaned_data:
                del self.cleaned_data[name]

    class Meta:
        exclude = ('user', 'anime', 'requestType', 'reason', 'status')

class FeedbackForm(RequestForm):
    text = CharField(label='Please tell about your suffering', widget=Textarea)
    class Meta:
        exclude = ('user', 'anime', 'requestType', 'reason', 'status')

EDIT_FORMS = {
    AnimeBundle: AnimeBundleForm,
    AnimeItem: AnimeForm,
    AnimeName: AnimeNameForm,
    UserStatusBundle: UserStatusForm,
    AnimeLinks: LinksForm,
    AnimeRequest: RequestForm,
    AnimeItemRequest: AnimeItemRequestForm,
    AnimeImageRequest: ImageRequestForm,
    AnimeFeedbackRequest: FeedbackForm,
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