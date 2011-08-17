from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, Textarea, FileField, \
                         BooleanField, CharField
from django.forms.forms import BoundField
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from anime.fields import TextToAnimeItemField, TextToAnimeNameField, UnknownDateField, \
                          CardImageField
from anime.models import AnimeBundle, AnimeItem, AnimeName, UserStatusBundle, AnimeLinks, AnimeRequest, \
                         AnimeItemRequest, AnimeImageRequest, AnimeFeedbackRequest
import os

class UserCreationFormMail(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationFormMail, self).__init__(*args, prefix='register', **kwargs)
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('username', 'email')

class NotActiveAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
        self.check_for_test_cookie()
        return self.cleaned_data

class ErrorForm(Form):
    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

class UploadMalListForm(ErrorForm):
    file = FileField(max_length=200)
    rewrite = BooleanField(label='Overwrite existing data', required=False)

class ReadOnlyModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.__readonly__ = False
        super(ReadOnlyModelForm, self).__init__(*args, **kwargs)

    def readonly(self):
        self.__readonly__ = True

    def writeable(self):
        self.__readonly__ = False

    def clean(self):
        if hasattr(self, '__readonly__') and self.__readonly__:
            raise ValidationError('This form is readonly for you.')
        return super(ReadOnlyModelForm, self).clean()

class ErrorModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        #FUUUU
        kwargs.pop('user', None)
        super(ErrorModelForm, self).__init__(*args, **kwargs)

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

class LinksForm(ErrorModelForm):
    class Meta:
        exclude = ('anime')

class RequestForm(ErrorModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        instance = kwargs.get('instance', None)
        super(RequestForm, self).__init__(*args, **kwargs)
        if instance and user:
            try:
                instance.user
            except:
                instance.user = user

    class Meta:
        exclude = ('user', 'anime', 'status')

class PureRequestForm(ReadOnlyModelForm, RequestForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.get('user', None)
        super(PureRequestForm, self).__init__(*args, **kwargs)
        if not user or not user.is_staff:
            self.readonly()

    def clean_status(self):
        if self.instance.requestType == 1 and self.instance.status > 0:
            if 'status' in self._get_changed_data():
                raise ValidationError('You cannot change it anymore.')
        return self.cleaned_data['status']

    class Meta:
        exclude = ('user', 'anime', 'text', 'requestType',)

class AnimeItemRequestForm(RequestForm):
    text = CharField(label="Request anime", widget=Textarea)
    class Meta:
        exclude = ('user', 'anime', 'requestType', 'reason', 'status')

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
    AnimeRequest: PureRequestForm,
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
