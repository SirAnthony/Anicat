from django.forms import ModelForm
from models import AnimeItem, UserStatusBundle

class AnimeForm(ModelForm):
    class Meta():
        model = AnimeItem
        exclude = ('bundle', 'air',)

class UserStatusForm(ModelForm):
    class Meta():
        model = UserStatusBundle
        exclude = ('anime', 'user')