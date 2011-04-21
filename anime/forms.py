from django.forms import Form, ModelForm, TextInput, FileField, DateTimeField, BooleanField
from models import AnimeItem, UserStatusBundle, AnimeLinks
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ErrorModelForm(ModelForm):
    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

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
    f = fields.split(',') if fields else None
    class _ModelForm(parent):
        class Meta(parent.Meta):
            model = m
            fields = f
    return _ModelForm