from django.forms import Form, ModelForm, TextInput, FileField, DateTimeField, BooleanField
from django.forms.forms import BoundField
from django.utils.encoding import force_unicode
from models import AnimeItem, UserStatusBundle, AnimeLinks
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.html import conditional_escape

class ErrorModelForm(ModelForm):
    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

    def as_json(self):
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []

        for name, field in self.fields.items():
            html_class_attr = None
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                css_classes = bf.css_classes()
                if css_classes:
                    html_class_attr = css_classes.split()

                if bf_errors:
                    output.append(force_unicode(bf_errors))

                if bf.label:
                    label = conditional_escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in
                    # punctuation.
                    if self.label_suffix:
                        if label[-1] not in ':?.!':
                            label += self.label_suffix
                    label = bf.label_tag(label) or ''
                else:
                    label = ''

                if field.help_text:
                    help_text = force_unicode(field.help_text)
                else:
                    help_text = u''

                output.append({
                    'errors': force_unicode(bf_errors),
                    'label': force_unicode(label),
                    'field': unicode(bf),
                    'help_text': help_text,
                    'html_class_attr': html_class_attr
                })

        if top_errors:
            output.insert(0, force_unicode(top_errors))
        if hidden_fields: # Insert any hidden fields in the last row.
            for field in hidden_fields:
                output.append(field)
        return output


    class Meta:
        pass

class ErrorForm(Form):
    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

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