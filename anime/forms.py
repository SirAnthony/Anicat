from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, ModelForm, TextInput, FileField, DateTimeField, BooleanField, ChoiceField
from django.forms.forms import BoundField
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from anime.models import AnimeBundle, AnimeItem, UserStatusBundle, AnimeLinks

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
        keys.sort()
        for k in keys:
            self.fields[k] = kwds[k]

    def setData(self, kwds):
        keys = kwds.keys()
        keys.sort()
        for name,field in self.fields.items():
            self.data[name] = field.widget.value_from_datadict(kwds, self.files, self.add_prefix(name))
        self.is_bound = True

class AnimeBundleForm(DynamicModelForm):

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(AnimeBundleForm, self).__init__(*args, **kwargs)
        if instance:
            if not isinstance(instance, AnimeBundle):
                raise TypeError('%s is not AnimeBundle instance.' % type(instance).__name__)
            anime = list(AnimeItem.objects.all().values_list('id', 'title'))
            anime.insert(0,['','----Remove----'])
            items = instance.animeitems.all()
            fields = {}
            for i in range(len(items) + 1):
                pass
                field = ChoiceField(choices=anime, required=False)
                #try:
                #    field.initial = [x for x in range(len(anime)) if anime[x][1] == items[i]][0]
                #except IndexError:
                #    pass
                fields['bundle%i' % i] = field
            self.setFields(fields)


class CalendarWidget(TextInput):
    class Media:
        js = ("calendar.js", "DateTimeShortcuts.js")

    def __init__(self, attrs={}):
        super(CalendarWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'})

class AnimeForm(ErrorModelForm):
    releasedAt = DateTimeField(label='Released', widget=CalendarWidget)
    endedAt = DateTimeField(label='Ended', widget=CalendarWidget, required=False)

    class Meta():
        model = AnimeItem
        exclude = ('bundle', 'locked')

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