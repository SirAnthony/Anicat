from django.forms import ModelForm, TextInput, DateTimeField, BooleanField
from models import AnimeItem, UserStatusBundle
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ErrorForm(ModelForm):
    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

class CalendarWidget(TextInput):
    class Media:
 	    js = ("calendar.js", "DateTimeShortcuts.js")
 	
    def __init__(self, attrs={}):
        super(CalendarWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'})

class AnimeForm(ErrorForm):
    releasedAt = DateTimeField(label='Released', widget=CalendarWidget)
    endedAt = DateTimeField(label='Ended', widget=CalendarWidget, required=False)
    
    class Meta():
        model = AnimeItem        
        exclude = ('bundle', 'locked')

class UserStatusForm(ModelForm):
    class Meta():
        model = UserStatusBundle
        exclude = ('anime', 'user')

class UserCreationFormMail(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationFormMail, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('username', 'email') 

